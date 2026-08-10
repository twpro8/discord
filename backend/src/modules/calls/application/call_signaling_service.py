import asyncio
import json
from collections.abc import Awaitable, Callable
from typing import Any
from uuid import UUID

from src.core.logging import get_logger
from src.core.realtime.envelope import EventType
from src.core.realtime.notifier import RealtimeNotifier
from src.core.realtime.rooms import connection_room, user_room
from src.modules.calls.domain.entities.call_session import CallSession
from src.modules.calls.domain.enums import CallState, ReserveOutcome
from src.modules.calls.domain.repositories.call_repository import CallRepository

logger = get_logger(__name__)

# Redis TTL headroom over the app-level ring timeout, so the ring-timeout
# task (which is the primary cleanup path) always fires before the Redis
# key itself would expire — the TTL is a crash backstop, not the normal
# cleanup mechanism.
_RING_TTL_BUFFER_SECONDS = 15.0

ListChatMemberIds = Callable[[UUID], Awaitable[set[UUID]]]
_Handler = Callable[[UUID, UUID, dict[str, Any]], Awaitable[None]]

_FRAME_TYPES = {
    "call.invite",
    "call.cancel",
    "call.accept",
    "call.reject",
    "call.hangup",
    "call.offer",
    "call.answer",
    "call.ice_candidate",
}


class CallSignalingService:
    """Stateless authenticated relay for 1:1 call signaling — mirrors
    TypingService's shape (modules.typing.application.typing_service) but,
    unlike typing, needs cross-instance busy/glare state (Redis, via
    CallRepository) and surfaces invite-authorization failures to the
    sender instead of silently dropping them: a silently-dropped invite
    would leave the caller's UI stuck ringing forever. Built once at app
    startup (main.py's lifespan), wired into ConnectionManager's activity
    callback alongside PresenceService/TypingService.

    Delivery targeting is entirely a room choice, never client-supplied
    data: events every one of a user's tabs should reflect (ringing state,
    call ended) go to user_room(user_id); events that must reach exactly
    the one tab running the RTCPeerConnection (offer/answer/ICE, and the
    losing side of a same-user double-accept race) go to
    connection_room(connection_id), using a connection_id the server
    always already has for free from on_activity's own parameters — no
    client ever learns or reports its own connection id. See plan §2.4.
    """

    def __init__(
        self,
        call_repository: CallRepository,
        realtime_notifier: RealtimeNotifier,
        list_chat_member_ids: ListChatMemberIds,
        *,
        ring_timeout_seconds: float,
        active_session_ttl_seconds: float,
    ) -> None:
        self._calls = call_repository
        self._notifier = realtime_notifier
        self._list_chat_member_ids = list_chat_member_ids
        self._ring_timeout_seconds = ring_timeout_seconds
        self._active_session_ttl_seconds = active_session_ttl_seconds
        # Strong references for detached ring-timeout tasks — asyncio only
        # holds a *weak* reference via the event loop, so without this a
        # task can be garbage-collected mid-sleep (same rationale as
        # api.v1.ws._background_tasks).
        self._timeout_tasks: set[asyncio.Task[None]] = set()
        self._handlers: dict[str, _Handler] = {
            "call.invite": self._handle_invite,
            "call.cancel": self._handle_cancel,
            "call.accept": self._handle_accept,
            "call.reject": self._handle_reject,
            "call.hangup": self._handle_hangup,
            "call.offer": self._handle_offer,
            "call.answer": self._handle_answer,
            "call.ice_candidate": self._handle_ice_candidate,
        }

    async def on_activity(
        self, user_id: UUID, connection_id: UUID, raw_text: str
    ) -> None:
        """Fires on every inbound frame; anything that isn't a recognized
        call.* frame is silently ignored (matches typing/presence's
        tolerance for frames they don't own). Any exception from a
        handler is caught here so one bad frame can never propagate up
        and disconnect the socket — the equivalent of TypingService's own
        top-level try/except, just wrapping the dispatch call instead of
        being duplicated inside every handler."""
        frame = _parse_frame(raw_text)
        if frame is None:
            return
        frame_type, payload = frame
        handler = self._handlers[frame_type]
        try:
            await handler(user_id, connection_id, payload)
        except Exception:
            logger.exception(
                "calls.on_activity_failed",
                frame_type=frame_type,
                user_id=str(user_id),
                connection_id=str(connection_id),
            )

    async def handle_disconnect(self, user_id: UUID, connection_id: UUID) -> None:
        """Ends the user's active call only if the disconnecting
        connection is the one actually pinned to it (caller_connection_id
        while RINGING, answering_connection_id once ACTIVE) — an
        uninvolved sibling tab of the same user disconnecting is a no-op.
        Documented asymmetry: during RINGING, only the caller's connection
        is pinned (the callee hasn't been decided yet), so a callee's last
        tab closing mid-ring isn't caught here — it's caught by the ring
        timeout instead. Deliberate v1 simplification (avoids needing
        ConnectionManager's per-user connection count exposed to this
        module), not an oversight."""
        call_id = await self._calls.get_active_call_id_for_user(user_id)
        if call_id is None:
            return
        session = await self._calls.get_session(call_id)
        if session is None:
            return
        is_pinned = (
            session.caller_id == user_id
            and session.caller_connection_id == connection_id
        ) or (
            session.callee_id == user_id
            and session.answering_connection_id == connection_id
        )
        if not is_pinned:
            return
        ended = await self._calls.end_session(call_id)
        if ended is None:
            return
        await self._broadcast_both(
            ended,
            EventType.CALL_HANGUP,
            {"call_id": str(call_id), "reason": "disconnected"},
        )

    async def get_pending_invite(self, user_id: UUID) -> dict[str, str] | None:
        """Returns the call.invite payload for a still-RINGING call where
        `user_id` is the callee, if any — covers the case a plain
        broadcast can't: `call.invite` published while the callee had
        zero open connections (offline) has no subscriber to reach at
        all, and Redis pub/sub keeps no history, so it's simply lost,
        not queued. Nothing would otherwise tell them a call started
        once they do come online.

        Deliberately a pure query, not a publish: the caller (ws.py) is
        expected to hand the result straight to the freshly (re)connected
        `Connection` it already holds via `Connection.send(...)`, not
        route it through `RealtimeNotifier`/a room. Publishing to that
        connection's own connection_room immediately after it joins would
        race the room's Redis subscription actually taking effect —
        `RedisSubscriptionManager.on_room_activated` only enqueues the
        SUBSCRIBE, it doesn't wait for it — so a message published in
        that same instant can arrive at Redis before any local
        subscriber exists for the channel and be silently dropped, the
        same "no history" semantics as the offline case this method
        exists to work around. A direct, same-process, no-Redis send
        sidesteps that race entirely, which a broadcast to a room this
        one connection just joined cannot."""
        call_id = await self._calls.get_active_call_id_for_user(user_id)
        if call_id is None:
            return None
        session = await self._calls.get_session(call_id)
        if (
            session is None
            or session.callee_id != user_id
            or session.state is not CallState.RINGING
        ):
            return None
        return {
            "call_id": str(session.call_id),
            "chat_id": str(session.chat_id),
            "caller_id": str(session.caller_id),
            "callee_id": str(session.callee_id),
        }

    async def _handle_invite(
        self, caller_id: UUID, connection_id: UUID, payload: dict[str, Any]
    ) -> None:
        call_id = _get_uuid(payload, "call_id")
        chat_id = _get_uuid(payload, "chat_id")
        callee_id = _get_uuid(payload, "callee_id")
        if call_id is None or chat_id is None or callee_id is None:
            return

        if caller_id == callee_id:
            await self._send_error(
                connection_id, call_id, "self_call", "Cannot call yourself"
            )
            return

        member_ids = await self._list_chat_member_ids(chat_id)
        if caller_id not in member_ids:
            await self._send_error(
                connection_id, call_id, "unauthorized", "Not a member of this chat"
            )
            return
        if callee_id not in member_ids or len(member_ids) != 2:
            await self._send_error(
                connection_id,
                call_id,
                "invalid_callee",
                "Callee is not the other member of this chat",
            )
            return

        outcome = await self._calls.reserve(
            call_id,
            chat_id,
            caller_id,
            callee_id,
            connection_id,
            ring_ttl_seconds=self._ring_timeout_seconds + _RING_TTL_BUFFER_SECONDS,
        )
        if outcome is ReserveOutcome.CALLER_BUSY:
            await self._send_busy(connection_id, call_id, "self_busy")
            return
        if outcome is ReserveOutcome.CALLEE_BUSY:
            await self._send_busy(connection_id, call_id, "callee_busy")
            return

        invite_payload = {
            "call_id": str(call_id),
            "chat_id": str(chat_id),
            "caller_id": str(caller_id),
            "callee_id": str(callee_id),
        }
        await self._notifier.publish_to_room(
            user_room(caller_id), EventType.CALL_INVITE, invite_payload
        )
        await self._notifier.publish_to_room(
            user_room(callee_id), EventType.CALL_INVITE, invite_payload
        )
        self._schedule_ring_timeout(call_id)

    async def _handle_cancel(
        self, user_id: UUID, connection_id: UUID, payload: dict[str, Any]
    ) -> None:
        call_id = _get_uuid(payload, "call_id")
        if call_id is None:
            return
        session = await self._calls.get_session(call_id)
        if (
            session is None
            or session.state is not CallState.RINGING
            or session.caller_id != user_id
        ):
            return
        ended = await self._calls.end_session(call_id)
        if ended is None:
            return
        await self._broadcast_both(
            ended, EventType.CALL_CANCELLED, {"call_id": str(call_id)}
        )

    async def _handle_reject(
        self, user_id: UUID, connection_id: UUID, payload: dict[str, Any]
    ) -> None:
        call_id = _get_uuid(payload, "call_id")
        if call_id is None:
            return
        session = await self._calls.get_session(call_id)
        if (
            session is None
            or session.state is not CallState.RINGING
            or session.callee_id != user_id
        ):
            return
        ended = await self._calls.end_session(call_id)
        if ended is None:
            return
        await self._broadcast_both(
            ended, EventType.CALL_REJECTED, {"call_id": str(call_id)}
        )

    async def _handle_hangup(
        self, user_id: UUID, connection_id: UUID, payload: dict[str, Any]
    ) -> None:
        call_id = _get_uuid(payload, "call_id")
        if call_id is None:
            return
        session = await self._calls.get_session(call_id)
        if session is None or user_id not in (session.caller_id, session.callee_id):
            return
        ended = await self._calls.end_session(call_id)
        if ended is None:
            return
        await self._broadcast_both(
            ended,
            EventType.CALL_HANGUP,
            {"call_id": str(call_id), "reason": "hangup"},
        )

    async def _handle_accept(
        self, user_id: UUID, connection_id: UUID, payload: dict[str, Any]
    ) -> None:
        call_id = _get_uuid(payload, "call_id")
        if call_id is None:
            return
        session = await self._calls.get_session(call_id)
        if session is None or session.callee_id != user_id:
            return
        if session.state is not CallState.RINGING:
            # Already resolved by the time we read it — in practice this
            # is always a same-user double-accept where another of the
            # callee's own tabs already won (a session that's been
            # rejected/cancelled/timed-out is deleted outright, never left
            # non-RINGING, so ACTIVE is the only other state reachable
            # here). This is the common case, not just a rare interleave:
            # there's no `await` between this read and try_accept()'s own
            # atomic marker below, so two accepts issued back-to-back
            # almost always resolve here rather than racing inside
            # try_accept — both paths must notify the loser the same way.
            await self._send_answered_elsewhere(connection_id, call_id)
            return
        won = await self._calls.try_accept(
            call_id, connection_id, active_ttl_seconds=self._active_session_ttl_seconds
        )
        if not won:
            # The genuinely-interleaved case: another accept's try_accept
            # won between our state read above and this call.
            await self._send_answered_elsewhere(connection_id, call_id)
            return
        await self._broadcast_both(
            session, EventType.CALL_ACCEPTED, {"call_id": str(call_id)}
        )

    async def _send_answered_elsewhere(
        self, connection_id: UUID, call_id: UUID
    ) -> None:
        # Only this specific losing tab needs to know — not the whole
        # user_room, which already got call.accepted from the winner.
        await self._notifier.publish_to_room(
            connection_room(connection_id),
            EventType.CALL_BUSY,
            {"call_id": str(call_id), "reason": "answered_elsewhere"},
        )

    async def _handle_offer(
        self, user_id: UUID, connection_id: UUID, payload: dict[str, Any]
    ) -> None:
        call_id = _get_uuid(payload, "call_id")
        sdp = payload.get("sdp")
        if call_id is None or sdp is None:
            return
        session = await self._calls.get_session(call_id)
        if (
            session is None
            or session.state is not CallState.ACTIVE
            or session.caller_connection_id != connection_id
            or session.answering_connection_id is None
        ):
            return
        await self._notifier.publish_to_room(
            connection_room(session.answering_connection_id),
            EventType.CALL_OFFER,
            {"call_id": str(call_id), "sdp": sdp},
        )

    async def _handle_answer(
        self, user_id: UUID, connection_id: UUID, payload: dict[str, Any]
    ) -> None:
        call_id = _get_uuid(payload, "call_id")
        sdp = payload.get("sdp")
        if call_id is None or sdp is None:
            return
        session = await self._calls.get_session(call_id)
        if (
            session is None
            or session.state is not CallState.ACTIVE
            or session.answering_connection_id != connection_id
        ):
            return
        await self._notifier.publish_to_room(
            connection_room(session.caller_connection_id),
            EventType.CALL_ANSWER,
            {"call_id": str(call_id), "sdp": sdp},
        )

    async def _handle_ice_candidate(
        self, user_id: UUID, connection_id: UUID, payload: dict[str, Any]
    ) -> None:
        call_id = _get_uuid(payload, "call_id")
        candidate = payload.get("candidate")
        if call_id is None or candidate is None:
            return
        session = await self._calls.get_session(call_id)
        if session is None or session.state is not CallState.ACTIVE:
            return
        if (
            connection_id == session.caller_connection_id
            and session.answering_connection_id is not None
        ):
            target = session.answering_connection_id
        elif connection_id == session.answering_connection_id:
            target = session.caller_connection_id
        else:
            return
        await self._notifier.publish_to_room(
            connection_room(target),
            EventType.CALL_ICE_CANDIDATE,
            {"call_id": str(call_id), "candidate": candidate},
        )

    def _schedule_ring_timeout(self, call_id: UUID) -> None:
        task = asyncio.create_task(self._ring_timeout(call_id))
        self._timeout_tasks.add(task)
        task.add_done_callback(self._timeout_tasks.discard)

    async def _ring_timeout(self, call_id: UUID) -> None:
        await asyncio.sleep(self._ring_timeout_seconds)
        session = await self._calls.get_session(call_id)
        if session is None or session.state is not CallState.RINGING:
            # Already accepted/rejected/cancelled — nothing to time out.
            return
        ended = await self._calls.end_session(call_id)
        if ended is None:
            return
        await self._broadcast_both(
            ended, EventType.CALL_TIMEOUT, {"call_id": str(call_id)}
        )

    async def _broadcast_both(
        self, session: CallSession, event_type: EventType, payload: dict[str, Any]
    ) -> None:
        await self._notifier.publish_to_room(
            user_room(session.caller_id), event_type, payload
        )
        await self._notifier.publish_to_room(
            user_room(session.callee_id), event_type, payload
        )

    async def _send_error(
        self, connection_id: UUID, call_id: UUID | None, code: str, message: str
    ) -> None:
        payload: dict[str, Any] = {"code": code, "message": message}
        if call_id is not None:
            payload["call_id"] = str(call_id)
        await self._notifier.publish_to_room(
            connection_room(connection_id), EventType.ERROR, payload
        )

    async def _send_busy(self, connection_id: UUID, call_id: UUID, reason: str) -> None:
        await self._notifier.publish_to_room(
            connection_room(connection_id),
            EventType.CALL_BUSY,
            {"call_id": str(call_id), "reason": reason},
        )


def _parse_frame(raw_text: str) -> tuple[str, dict[str, Any]] | None:
    # Broad except is deliberate — see typing_service._parse_typing_frame's
    # docstring for the pinned-ruff-formatter-bug rationale (applies
    # verbatim: any malformed/unexpected frame is meant to be treated as
    # "not recognized" here, not narrowed to specific exception types).
    try:
        data = json.loads(raw_text)
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    frame_type = data.get("type")
    if frame_type not in _FRAME_TYPES:
        return None
    return frame_type, data


def _get_uuid(data: dict[str, Any], key: str) -> UUID | None:
    try:
        return UUID(str(data[key]))
    except Exception:
        return None
