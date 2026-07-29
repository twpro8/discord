from dataclasses import dataclass
from uuid import UUID

from src.modules.friends.domain.exceptions import (
    FriendRequestNotFoundError,
    NotParticipantError,
)
from src.modules.friends.domain.repositories.friend_unit_of_work import (
    FriendUnitOfWork,
)
from src.shared.application.command import Command
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class DeleteFriendRequestCommand(Command):
    current_user_id: UUID
    request_id: UUID


class DeleteFriendRequestCommandHandler:
    def __init__(self, uow: FriendUnitOfWork) -> None:
        self._uow = uow

    async def handle(
        self, command: DeleteFriendRequestCommand
    ) -> Result[None, LumiereError]:
        request = await self._uow.friends.get_by_id(command.request_id)
        if request is None:
            return Result.err(FriendRequestNotFoundError())

        if (
            request.user_id != command.current_user_id
            and request.target_user_id != command.current_user_id
        ):
            return Result.err(NotParticipantError())

        await self._uow.friends.delete(command.request_id)
        await self._uow.commit()
        return Result.ok(None)
