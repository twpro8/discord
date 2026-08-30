from uuid import UUID

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.friends.domain.enums import FriendStatus
from src.modules.friends.adapters.persistence.models import FriendOrm
from src.modules.users.domain.entities.user import User


async def test_send_friend_request_creates_pending_relationship(
    authed_client: AsyncClient,
    current_user: User,
    get_all_users: list[User],
    session: AsyncSession,
) -> None:
    target_user = next(user for user in get_all_users if user.id != current_user.id)

    response = await authed_client.post(
        "/api/v1/friends/requests",
        json={"username": target_user.username},
    )

    assert response.status_code == 201
    response_data = response.json()
    assert response_data["user_id"] == str(current_user.id)
    assert response_data["target_user_id"] == str(target_user.id)
    assert response_data["status"] == FriendStatus.PENDING

    request_id = UUID(response_data["id"])
    persisted_request = await session.scalar(
        select(FriendOrm).where(FriendOrm.id == request_id)
    )
    assert persisted_request is not None
    assert persisted_request.status == FriendStatus.PENDING


async def test_send_friend_request_rejects_duplicate_relationship(
    authed_client: AsyncClient,
    get_all_users: list[User],
) -> None:
    target_user = get_all_users[2]
    payload = {"username": target_user.username}

    first_response = await authed_client.post("/api/v1/friends/requests", json=payload)
    second_response = await authed_client.post("/api/v1/friends/requests", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


async def test_send_friend_request_rejects_self_request(
    authed_client: AsyncClient,
    current_user: User,
) -> None:
    response = await authed_client.post(
        "/api/v1/friends/requests",
        json={"username": current_user.username},
    )

    assert response.status_code == 400


async def test_send_friend_request_rejects_unknown_username(
    authed_client: AsyncClient,
) -> None:
    response = await authed_client.post(
        "/api/v1/friends/requests",
        json={"username": "unknown_user"},
    )

    assert response.status_code == 404
