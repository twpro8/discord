from dataclasses import dataclass
from uuid import UUID

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
class RemoveFriendCommand(Command):
    current_user_id: UUID
    relationship_id: UUID


class RemoveFriendCommandHandler:
    def __init__(self, uow: FriendUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: RemoveFriendCommand) -> Result[None, LumiereError]:
        request = await self._uow.friends.get_by_id(command.relationship_id)
        if request is None:
            return Result.err(FriendRequestNotFoundError())

        if (
            request.user_id != command.current_user_id
            and request.target_user_id != command.current_user_id
        ):
            return Result.err(NotParticipantError())

        if request.status != FriendStatus.FRIENDS:
            return Result.err(FriendRequestNotPendingError())

        await self._uow.friends.delete(command.relationship_id)
        await self._uow.commit()
        return Result.ok(None)
