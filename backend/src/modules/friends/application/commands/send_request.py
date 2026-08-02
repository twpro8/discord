from dataclasses import dataclass
from uuid import UUID

from src.modules.friends.domain.entities.dtos import (
    FriendRequestCreate,
    SendFriendRequestData,
)
from src.modules.friends.domain.entities.friend_request import FriendRequest
from src.modules.friends.domain.exceptions import (
    CannotSendFriendRequestToSelfError,
    FriendRequestAlreadyExistsError,
    TargetUserNotFoundError,
)
from src.modules.friends.domain.repositories.friend_unit_of_work import (
    FriendUnitOfWork,
)
from src.modules.users.public.facade import UsersFacade
from src.shared.application.command import Command
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class SendFriendRequestCommand(Command):
    sender_id: UUID
    data: SendFriendRequestData


class SendFriendRequestCommandHandler:
    def __init__(self, uow: FriendUnitOfWork, users_facade: UsersFacade) -> None:
        self._uow = uow
        self._users_facade = users_facade

    async def handle(
        self, command: SendFriendRequestCommand
    ) -> Result[FriendRequest, LumiereError]:
        sender_id, data = command.sender_id, command.data
        target_user = await self._users_facade.get_user_by_username(data.username)
        if not target_user:
            return Result.err(TargetUserNotFoundError())

        if sender_id == target_user.id:
            return Result.err(CannotSendFriendRequestToSelfError())

        relationship = await self._uow.friends.get_between_users(
            sender_id, target_user.id
        )
        if relationship is not None:
            return Result.err(FriendRequestAlreadyExistsError())

        request = await self._uow.friends.create(
            FriendRequestCreate(user_id=sender_id, target_user_id=target_user.id)
        )
        await self._uow.commit()
        return Result.ok(request)
