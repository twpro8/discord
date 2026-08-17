import asyncio
import json
from uuid import UUID, uuid4

from src.core.realtime.envelope import EventType
from src.core.realtime.rooms import connection_room, user_room
from src.modules.calls.application.call_signaling_service import CallSignalingService
from tests.unit.calls.fakes import FakeCallRepository, FakeRealtimeNotifier


def _make_service(
    notifier: FakeRealtimeNotifier,
    repo: FakeCallRepository,
    *,
    members: dict[UUID, set[UUID]] | None = None,
    ring_timeout_seconds: float = 1000.0,
    active_session_ttl_seconds: float = 1000.0,
) -> CallSignalingService:
    members = members or {}

    async def list_chat_member_ids(chat_id: UUID) -> set[UUID]:
        return members.get(chat_id, set())

    return CallSignalingService(
        repo,
        notifier,
        list_chat_member_ids,
        ring_timeout_seconds=ring_timeout_seconds,
        active_session_ttl_seconds=active_session_ttl_seconds,
    )


def _frame(type_: str, **fields: object) -> str:
    return json.dumps({"type": type_, **fields})


async def test_full_happy_path_publishes_expected_sequence() -> None:
    notifier = FakeRealtimeNotifier()
    repo = FakeCallRepository()
    caller_id, callee_id, chat_id = uuid4(), uuid4(), uuid4()
    caller_conn, callee_conn = uuid4(), uuid4()
    call_id = uuid4()
    service = _make_service(notifier, repo, members={chat_id: {caller_id, callee_id}})

    await service.on_activity(
        caller_id,
        caller_conn,
        _frame(
            "call.invite",
            call_id=str(call_id),
            chat_id=str(chat_id),
            callee_id=str(callee_id),
        ),
    )
    await service.on_activity(
        callee_id, callee_conn, _frame("call.accept", call_id=str(call_id))
    )
    await service.on_activity(
        caller_id,
        caller_conn,
        _frame("call.offer", call_id=str(call_id), sdp={"type": "offer"}),
    )
    await service.on_activity(
        callee_id,
        callee_conn,
        _frame("call.answer", call_id=str(call_id), sdp={"type": "answer"}),
    )
    await service.on_activity(
        caller_id,
        caller_conn,
        _frame(
            "call.ice_candidate", call_id=str(call_id), candidate={"candidate": "x"}
        ),
    )
    await service.on_activity(
        caller_id,
        caller_conn,
        _frame(
            "call.media_state",
            call_id=str(call_id),
            video_camera=False,
            video_screen=False,
        ),
    )
    await service.on_activity(
        caller_id, caller_conn, _frame("call.hangup", call_id=str(call_id))
    )

    invite_payload = {
        "call_id": str(call_id),
        "chat_id": str(chat_id),
        "caller_id": str(caller_id),
        "callee_id": str(callee_id),
    }
    assert notifier.published == [
        (user_room(caller_id), EventType.CALL_INVITE, invite_payload),
        (user_room(callee_id), EventType.CALL_INVITE, invite_payload),
        (user_room(caller_id), EventType.CALL_ACCEPTED, {"call_id": str(call_id)}),
        (user_room(callee_id), EventType.CALL_ACCEPTED, {"call_id": str(call_id)}),
        (
            connection_room(callee_conn),
            EventType.CALL_OFFER,
            {"call_id": str(call_id), "sdp": {"type": "offer"}},
        ),
        (
            connection_room(caller_conn),
            EventType.CALL_ANSWER,
            {"call_id": str(call_id), "sdp": {"type": "answer"}},
        ),
        (
            connection_room(callee_conn),
            EventType.CALL_ICE_CANDIDATE,
            {"call_id": str(call_id), "candidate": {"candidate": "x"}},
        ),
        (
            connection_room(callee_conn),
            EventType.CALL_MEDIA_STATE,
            {
                "call_id": str(call_id),
                "video_camera": False,
                "video_screen": False,
            },
        ),
        (
            user_room(caller_id),
            EventType.CALL_HANGUP,
            {"call_id": str(call_id), "reason": "hangup"},
        ),
        (
            user_room(callee_id),
            EventType.CALL_HANGUP,
            {"call_id": str(call_id), "reason": "hangup"},
        ),
    ]
    assert repo.sessions == {}
    assert repo.active_user == {}


async def test_answerer_initiated_renegotiation_relays_both_ways() -> None:
    notifier = FakeRealtimeNotifier()
    repo = FakeCallRepository()
    caller_id, callee_id, chat_id = uuid4(), uuid4(), uuid4()
    caller_conn, callee_conn = uuid4(), uuid4()
    call_id = uuid4()
    service = _make_service(notifier, repo, members={chat_id: {caller_id, callee_id}})

    await service.on_activity(
        caller_id,
        caller_conn,
        _frame(
            "call.invite",
            call_id=str(call_id),
            chat_id=str(chat_id),
            callee_id=str(callee_id),
        ),
    )
    await service.on_activity(
        callee_id, callee_conn, _frame("call.accept", call_id=str(call_id))
    )
    notifier.published.clear()

    # Mid-call renegotiation initiated by the *answerer* (e.g. adding a
    # video track for camera/screen share): the offer relays to the
    # caller's pinned connection and the caller's answer back to the
    # answerer's — the relay is symmetric over the two pinned rooms, not
    # fixed to the initial offerer.
    await service.on_activity(
        callee_id,
        callee_conn,
        _frame("call.offer", call_id=str(call_id), sdp={"type": "offer"}),
    )
    await service.on_activity(
        caller_id,
        caller_conn,
        _frame("call.answer", call_id=str(call_id), sdp={"type": "answer"}),
    )

    assert notifier.published == [
        (
            connection_room(caller_conn),
            EventType.CALL_OFFER,
            {"call_id": str(call_id), "sdp": {"type": "offer"}},
        ),
        (
            connection_room(callee_conn),
            EventType.CALL_ANSWER,
            {"call_id": str(call_id), "sdp": {"type": "answer"}},
        ),
    ]


async def test_media_state_relays_both_ways_without_parsing_the_payload() -> None:
    notifier = FakeRealtimeNotifier()
    repo = FakeCallRepository()
    caller_id, callee_id, chat_id = uuid4(), uuid4(), uuid4()
    caller_conn, callee_conn = uuid4(), uuid4()
    call_id = uuid4()
    service = _make_service(notifier, repo, members={chat_id: {caller_id, callee_id}})

    await service.on_activity(
        caller_id,
        caller_conn,
        _frame(
            "call.invite",
            call_id=str(call_id),
            chat_id=str(chat_id),
            callee_id=str(callee_id),
        ),
    )
    await service.on_activity(
        callee_id, callee_conn, _frame("call.accept", call_id=str(call_id))
    )
    notifier.published.clear()

    # Camera/screen share state is relayed verbatim (server never parses
    # it beyond call_id) to whichever pinned connection holds the peer's
    # RTCPeerConnection — symmetric over the two pinned rooms, like offer/
    # answer — so future media flags reach the peer without backend changes.
    await service.on_activity(
        caller_id,
        caller_conn,
        _frame(
            "call.media_state",
            call_id=str(call_id),
            video_camera=True,
            video_screen=False,
        ),
    )
    await service.on_activity(
        callee_id,
        callee_conn,
        _frame(
            "call.media_state",
            call_id=str(call_id),
            video_camera=False,
            video_screen=True,
        ),
    )

    assert notifier.published == [
        (
            connection_room(callee_conn),
            EventType.CALL_MEDIA_STATE,
            {"call_id": str(call_id), "video_camera": True, "video_screen": False},
        ),
        (
            connection_room(caller_conn),
            EventType.CALL_MEDIA_STATE,
            {"call_id": str(call_id), "video_camera": False, "video_screen": True},
        ),
    ]


async def test_invite_while_callee_busy_reports_callee_busy_and_creates_no_session() -> (
    None
):
    notifier = FakeRealtimeNotifier()
    repo = FakeCallRepository()
    caller_id, callee_id, chat_id = uuid4(), uuid4(), uuid4()
    caller_conn = uuid4()
    call_id = uuid4()
    service = _make_service(notifier, repo, members={chat_id: {caller_id, callee_id}})
    # Put callee_id in an unrelated active call first.
    repo.active_user[callee_id] = uuid4()

    await service.on_activity(
        caller_id,
        caller_conn,
        _frame(
            "call.invite",
            call_id=str(call_id),
            chat_id=str(chat_id),
            callee_id=str(callee_id),
        ),
    )

    assert notifier.published == [
        (
            connection_room(caller_conn),
            EventType.CALL_BUSY,
            {"call_id": str(call_id), "reason": "callee_busy"},
        )
    ]
    assert call_id not in repo.sessions


async def test_invite_while_caller_busy_reports_self_busy() -> None:
    notifier = FakeRealtimeNotifier()
    repo = FakeCallRepository()
    caller_id, callee_id, chat_id = uuid4(), uuid4(), uuid4()
    caller_conn = uuid4()
    call_id = uuid4()
    service = _make_service(notifier, repo, members={chat_id: {caller_id, callee_id}})
    repo.active_user[caller_id] = uuid4()

    await service.on_activity(
        caller_id,
        caller_conn,
        _frame(
            "call.invite",
            call_id=str(call_id),
            chat_id=str(chat_id),
            callee_id=str(callee_id),
        ),
    )

    assert notifier.published == [
        (
            connection_room(caller_conn),
            EventType.CALL_BUSY,
            {"call_id": str(call_id), "reason": "self_busy"},
        )
    ]


async def test_invite_by_non_chat_member_is_unauthorized() -> None:
    notifier = FakeRealtimeNotifier()
    repo = FakeCallRepository()
    caller_id, callee_id, chat_id = uuid4(), uuid4(), uuid4()
    caller_conn = uuid4()
    call_id = uuid4()
    # caller_id deliberately not in the chat's members.
    service = _make_service(notifier, repo, members={chat_id: {callee_id, uuid4()}})

    await service.on_activity(
        caller_id,
        caller_conn,
        _frame(
            "call.invite",
            call_id=str(call_id),
            chat_id=str(chat_id),
            callee_id=str(callee_id),
        ),
    )

    assert len(notifier.published) == 1
    room, event_type, payload = notifier.published[0]
    assert room == connection_room(caller_conn)
    assert event_type == EventType.ERROR
    assert payload["code"] == "unauthorized"
    assert call_id not in repo.sessions


async def test_invite_targeting_wrong_callee_in_a_private_chat_is_invalid_callee() -> (
    None
):
    notifier = FakeRealtimeNotifier()
    repo = FakeCallRepository()
    caller_id, real_peer_id, wrong_target_id, chat_id = (
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
    )
    caller_conn = uuid4()
    call_id = uuid4()
    # chat only has caller_id + real_peer_id — wrong_target_id isn't in it.
    service = _make_service(
        notifier, repo, members={chat_id: {caller_id, real_peer_id}}
    )

    await service.on_activity(
        caller_id,
        caller_conn,
        _frame(
            "call.invite",
            call_id=str(call_id),
            chat_id=str(chat_id),
            callee_id=str(wrong_target_id),
        ),
    )

    room, event_type, payload = notifier.published[0]
    assert event_type == EventType.ERROR
    assert payload["code"] == "invalid_callee"


async def test_invite_in_a_group_chat_is_rejected_as_invalid_callee() -> None:
    notifier = FakeRealtimeNotifier()
    repo = FakeCallRepository()
    caller_id, callee_id, third_member_id, chat_id = uuid4(), uuid4(), uuid4(), uuid4()
    caller_conn = uuid4()
    call_id = uuid4()
    # Callee IS a real member, but the chat has 3 members total.
    service = _make_service(
        notifier, repo, members={chat_id: {caller_id, callee_id, third_member_id}}
    )

    await service.on_activity(
        caller_id,
        caller_conn,
        _frame(
            "call.invite",
            call_id=str(call_id),
            chat_id=str(chat_id),
            callee_id=str(callee_id),
        ),
    )

    room, event_type, payload = notifier.published[0]
    assert event_type == EventType.ERROR
    assert payload["code"] == "invalid_callee"
    assert call_id not in repo.sessions


async def test_self_call_invite_is_rejected_without_touching_redis() -> None:
    notifier = FakeRealtimeNotifier()
    repo = FakeCallRepository()
    user_id, chat_id = uuid4(), uuid4()
    conn = uuid4()
    call_id = uuid4()
    service = _make_service(notifier, repo, members={chat_id: {user_id}})

    await service.on_activity(
        user_id,
        conn,
        _frame(
            "call.invite",
            call_id=str(call_id),
            chat_id=str(chat_id),
            callee_id=str(user_id),
        ),
    )

    room, event_type, payload = notifier.published[0]
    assert event_type == EventType.ERROR
    assert payload["code"] == "self_call"
    assert repo.sessions == {}
    assert repo.active_user == {}


async def test_accept_reject_hangup_offer_answer_ice_from_non_participant_are_dropped() -> (
    None
):
    notifier = FakeRealtimeNotifier()
    repo = FakeCallRepository()
    caller_id, callee_id, chat_id, stranger_id = uuid4(), uuid4(), uuid4(), uuid4()
    caller_conn, stranger_conn = uuid4(), uuid4()
    call_id = uuid4()
    service = _make_service(notifier, repo, members={chat_id: {caller_id, callee_id}})

    await service.on_activity(
        caller_id,
        caller_conn,
        _frame(
            "call.invite",
            call_id=str(call_id),
            chat_id=str(chat_id),
            callee_id=str(callee_id),
        ),
    )
    notifier.published.clear()

    for frame_type, extra in (
        ("call.accept", {}),
        ("call.reject", {}),
        ("call.cancel", {}),
        ("call.hangup", {}),
        ("call.offer", {"sdp": {"type": "offer"}}),
        ("call.answer", {"sdp": {"type": "answer"}}),
        ("call.ice_candidate", {"candidate": {"candidate": "x"}}),
        ("call.media_state", {"video_camera": True, "video_screen": False}),
    ):
        await service.on_activity(
            stranger_id,
            stranger_conn,
            _frame(frame_type, call_id=str(call_id), **extra),
        )

    assert notifier.published == []
    # Session must still be intact — none of the stranger's frames acted on it.
    assert call_id in repo.sessions


async def test_signaling_for_missing_session_is_dropped() -> None:
    notifier = FakeRealtimeNotifier()
    repo = FakeCallRepository()
    caller_id = uuid4()
    caller_conn = uuid4()
    call_id = uuid4()  # never reserved

    service = _make_service(notifier, repo)

    for frame_type, extra in (
        ("call.accept", {}),
        ("call.reject", {}),
        ("call.cancel", {}),
        ("call.hangup", {}),
        ("call.offer", {"sdp": {"type": "offer"}}),
        ("call.answer", {"sdp": {"type": "answer"}}),
        ("call.ice_candidate", {"candidate": {"candidate": "x"}}),
        ("call.media_state", {"video_camera": True, "video_screen": False}),
    ):
        await service.on_activity(
            caller_id, caller_conn, _frame(frame_type, call_id=str(call_id), **extra)
        )

    assert notifier.published == []


async def test_double_accept_race_only_one_tab_wins() -> None:
    notifier = FakeRealtimeNotifier()
    repo = FakeCallRepository()
    caller_id, callee_id, chat_id = uuid4(), uuid4(), uuid4()
    caller_conn = uuid4()
    callee_tab_a, callee_tab_b = uuid4(), uuid4()
    call_id = uuid4()
    service = _make_service(notifier, repo, members={chat_id: {caller_id, callee_id}})

    await service.on_activity(
        caller_id,
        caller_conn,
        _frame(
            "call.invite",
            call_id=str(call_id),
            chat_id=str(chat_id),
            callee_id=str(callee_id),
        ),
    )
    notifier.published.clear()

    await service.on_activity(
        callee_id, callee_tab_a, _frame("call.accept", call_id=str(call_id))
    )
    await service.on_activity(
        callee_id, callee_tab_b, _frame("call.accept", call_id=str(call_id))
    )

    assert notifier.published == [
        (user_room(caller_id), EventType.CALL_ACCEPTED, {"call_id": str(call_id)}),
        (user_room(callee_id), EventType.CALL_ACCEPTED, {"call_id": str(call_id)}),
        (
            connection_room(callee_tab_b),
            EventType.CALL_BUSY,
            {"call_id": str(call_id), "reason": "answered_elsewhere"},
        ),
    ]
    session = repo.sessions[call_id]
    assert session.answering_connection_id == callee_tab_a

    # The losing tab's offer/answer path is now inert too: an offer sent
    # by the caller only ever targets the winning connection.
    await service.on_activity(
        caller_id,
        caller_conn,
        _frame("call.offer", call_id=str(call_id), sdp={"type": "offer"}),
    )
    assert notifier.published[-1] == (
        connection_room(callee_tab_a),
        EventType.CALL_OFFER,
        {"call_id": str(call_id), "sdp": {"type": "offer"}},
    )


async def test_ring_timeout_fires_call_timeout_when_still_ringing() -> None:
    notifier = FakeRealtimeNotifier()
    repo = FakeCallRepository()
    caller_id, callee_id, chat_id = uuid4(), uuid4(), uuid4()
    caller_conn = uuid4()
    call_id = uuid4()
    service = _make_service(
        notifier,
        repo,
        members={chat_id: {caller_id, callee_id}},
        ring_timeout_seconds=0.02,
    )

    await service.on_activity(
        caller_id,
        caller_conn,
        _frame(
            "call.invite",
            call_id=str(call_id),
            chat_id=str(chat_id),
            callee_id=str(callee_id),
        ),
    )
    await asyncio.sleep(0.1)

    assert (
        user_room(caller_id),
        EventType.CALL_TIMEOUT,
        {"call_id": str(call_id)},
    ) in notifier.published
    assert call_id not in repo.sessions


async def test_ring_timeout_is_a_noop_once_accepted() -> None:
    notifier = FakeRealtimeNotifier()
    repo = FakeCallRepository()
    caller_id, callee_id, chat_id = uuid4(), uuid4(), uuid4()
    caller_conn, callee_conn = uuid4(), uuid4()
    call_id = uuid4()
    service = _make_service(
        notifier,
        repo,
        members={chat_id: {caller_id, callee_id}},
        ring_timeout_seconds=0.02,
    )

    await service.on_activity(
        caller_id,
        caller_conn,
        _frame(
            "call.invite",
            call_id=str(call_id),
            chat_id=str(chat_id),
            callee_id=str(callee_id),
        ),
    )
    await service.on_activity(
        callee_id, callee_conn, _frame("call.accept", call_id=str(call_id))
    )
    await asyncio.sleep(0.1)

    assert all(
        event_type != EventType.CALL_TIMEOUT for _, event_type, _ in notifier.published
    )
    assert call_id in repo.sessions


async def test_disconnect_ends_call_only_for_the_pinned_connection() -> None:
    notifier = FakeRealtimeNotifier()
    repo = FakeCallRepository()
    caller_id, callee_id, chat_id = uuid4(), uuid4(), uuid4()
    caller_conn, callee_other_tab = uuid4(), uuid4()
    call_id = uuid4()
    service = _make_service(notifier, repo, members={chat_id: {caller_id, callee_id}})

    await service.on_activity(
        caller_id,
        caller_conn,
        _frame(
            "call.invite",
            call_id=str(call_id),
            chat_id=str(chat_id),
            callee_id=str(callee_id),
        ),
    )
    notifier.published.clear()

    # An uninvolved sibling tab of the callee (never accepted) disconnecting
    # must not touch the still-ringing call.
    await service.handle_disconnect(callee_id, callee_other_tab)
    assert notifier.published == []
    assert call_id in repo.sessions

    # The caller's own (pinned) connection disconnecting does end it.
    await service.handle_disconnect(caller_id, caller_conn)
    assert (
        user_room(callee_id),
        EventType.CALL_HANGUP,
        {"call_id": str(call_id), "reason": "disconnected"},
    ) in notifier.published
    assert call_id not in repo.sessions


async def test_get_pending_invite_returns_the_invite_payload_for_the_callee() -> None:
    notifier = FakeRealtimeNotifier()
    repo = FakeCallRepository()
    caller_id, callee_id, chat_id = uuid4(), uuid4(), uuid4()
    caller_conn = uuid4()
    call_id = uuid4()
    service = _make_service(notifier, repo, members={chat_id: {caller_id, callee_id}})

    # Callee is offline: call.invite is "published" (no subscriber, but
    # the fake still records it) while the callee has no connection at
    # all — the scenario this resync exists to cover.
    await service.on_activity(
        caller_id,
        caller_conn,
        _frame(
            "call.invite",
            call_id=str(call_id),
            chat_id=str(chat_id),
            callee_id=str(callee_id),
        ),
    )
    notifier.published.clear()

    payload = await service.get_pending_invite(callee_id)

    # A pure query — never published anywhere; ws.py is responsible for
    # handing this directly to the connection that just asked.
    assert notifier.published == []
    assert payload == {
        "call_id": str(call_id),
        "chat_id": str(chat_id),
        "caller_id": str(caller_id),
        "callee_id": str(callee_id),
    }


async def test_get_pending_invite_is_none_with_no_active_call() -> None:
    notifier = FakeRealtimeNotifier()
    repo = FakeCallRepository()

    service = _make_service(notifier, repo)

    assert await service.get_pending_invite(uuid4()) is None


async def test_get_pending_invite_is_none_for_the_caller_reconnecting() -> None:
    notifier = FakeRealtimeNotifier()
    repo = FakeCallRepository()
    caller_id, callee_id, chat_id = uuid4(), uuid4(), uuid4()
    caller_conn = uuid4()
    call_id = uuid4()
    service = _make_service(notifier, repo, members={chat_id: {caller_id, callee_id}})

    await service.on_activity(
        caller_id,
        caller_conn,
        _frame(
            "call.invite",
            call_id=str(call_id),
            chat_id=str(chat_id),
            callee_id=str(callee_id),
        ),
    )

    # The caller reconnecting (e.g. a second tab) must not be resent
    # their own invite — resync exists only for the callee side.
    assert await service.get_pending_invite(caller_id) is None


async def test_get_pending_invite_is_none_once_the_call_is_no_longer_ringing() -> None:
    notifier = FakeRealtimeNotifier()
    repo = FakeCallRepository()
    caller_id, callee_id, chat_id = uuid4(), uuid4(), uuid4()
    caller_conn, callee_conn = uuid4(), uuid4()
    call_id = uuid4()
    service = _make_service(notifier, repo, members={chat_id: {caller_id, callee_id}})

    await service.on_activity(
        caller_id,
        caller_conn,
        _frame(
            "call.invite",
            call_id=str(call_id),
            chat_id=str(chat_id),
            callee_id=str(callee_id),
        ),
    )
    await service.on_activity(
        callee_id, callee_conn, _frame("call.accept", call_id=str(call_id))
    )

    assert await service.get_pending_invite(callee_id) is None


async def test_late_signaling_after_hangup_is_dropped() -> None:
    notifier = FakeRealtimeNotifier()
    repo = FakeCallRepository()
    caller_id, callee_id, chat_id = uuid4(), uuid4(), uuid4()
    caller_conn, callee_conn = uuid4(), uuid4()
    call_id = uuid4()
    service = _make_service(notifier, repo, members={chat_id: {caller_id, callee_id}})

    await service.on_activity(
        caller_id,
        caller_conn,
        _frame(
            "call.invite",
            call_id=str(call_id),
            chat_id=str(chat_id),
            callee_id=str(callee_id),
        ),
    )
    await service.on_activity(
        callee_id, callee_conn, _frame("call.accept", call_id=str(call_id))
    )
    await service.on_activity(
        caller_id, caller_conn, _frame("call.hangup", call_id=str(call_id))
    )
    notifier.published.clear()

    # A straggling ICE candidate arriving after the call already ended
    # must not resurrect any state or publish anything.
    await service.on_activity(
        callee_id,
        callee_conn,
        _frame(
            "call.ice_candidate", call_id=str(call_id), candidate={"candidate": "late"}
        ),
    )

    assert notifier.published == []
    assert call_id not in repo.sessions
