"""Integration test proving WS connect-time auto-join resolves a user's
existing chat memberships via the real DB-backed query path (not a fake)."""

from uuid import UUID, uuid4

from httpx import AsyncClient

from src.api.v1.ws import _resolve_active_chat_rooms
from src.core.database.session import get_null_pool_session_factory
from src.core.realtime.rooms import chat_room
from src.modules.chats.domain.enums import ChatType
from src.modules.users.domain.entities.user import User

# Bypassing FastAPI's DI here (calling the helper directly, not through a
# route) means the get_session_factory_ws override in conftest.py doesn't
# apply — pass the NullPool factory explicitly for the same reason it's
# used there: the production factory's pooled asyncpg connections are
# bound to the event loop active when first used, which breaks under
# pytest-asyncio's per-test event loops.
_session_factory = get_null_pool_session_factory()


async def test_resolve_active_chat_rooms_returns_rooms_for_existing_memberships(
    authed_client: AsyncClient,
    current_user: User,
    get_all_users: list[User],
) -> None:
    peer = next(u for u in get_all_users if u.id != current_user.id)

    response = await authed_client.post(
        "/api/v1/chats",
        json={"type": ChatType.private, "target_user_id": str(peer.id)},
    )
    assert response.status_code == 201
    chat_id = UUID(response.json()["id"])

    rooms = await _resolve_active_chat_rooms(current_user.id, _session_factory)

    # `in`, not `==`: current_user is a fixed seeded user shared across
    # the whole session (no per-test transaction rollback in this
    # suite), so other tests may have already given it other chats.
    assert chat_room(chat_id) in rooms


async def test_resolve_active_chat_rooms_is_empty_for_a_user_with_no_chats() -> None:
    # A fresh, never-seeded id — trivially zero rows regardless of what
    # other tests have done to the shared session-scoped DB (no
    # per-test transaction rollback in this suite's fixtures).
    rooms = await _resolve_active_chat_rooms(uuid4(), _session_factory)

    assert rooms == set()
