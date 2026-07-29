from dataclasses import dataclass
from uuid import UUID

from src.modules.friends.domain.entities.schemas import (
    FriendRequest,
    FriendRequestUpdate,
)
from src.modules.friends.domain.enums import FriendStatus
from src.modules.friends.domain.exceptions import (
    FriendRequestNotFoundError,
    FriendRequestNotPendingError,
    NotParticipantError,
)
from src.modules.friends.domain.repositories.friend_unit_of_work import (
    FriendUnitOfWork,
)
from src.shared.application.command import Command
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class AcceptFriendRequestCommand(Command):
    current_user_id: UUID
    request_id: UUID


class AcceptFriendRequestCommandHandler:
    def __init__(self, uow: FriendUnitOfWork) -> None:
        self._uow = uow

    async def handle(
        self, command: AcceptFriendRequestCommand
    ) -> Result[FriendRequest, LumiereError]:
        request = await self._uow.friends.get_by_id(command.request_id)
        if request is None:
            return Result.err(FriendRequestNotFoundError())

        if request.target_user_id != command.current_user_id:
            return Result.err(NotParticipantError())

        if request.status != FriendStatus.PENDING:
            return Result.err(FriendRequestNotPendingError())

        updated = await self._uow.friends.update(
            command.request_id,
            FriendRequestUpdate(status=FriendStatus.FRIENDS),
        )
        await self._uow.commit()
        return Result.ok(updated)
