import secrets
import string
from datetime import UTC, datetime, timedelta
from typing import Literal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.common.services.base_service import BaseService
from src.modules.servers.invites.exceptions import (
    ServerInviteCannotDeleteError,
    ServerInviteGenerationFailedError,
    ServerInviteNotFoundError,
    ServerInvitePermissionDeniedError,
)
from src.modules.servers.invites.schemas import (
    CreateServerInvite,
    CreateServerInviteRequest,
    ServerInvite,
    ServerInviteWithStatus,
)
from src.modules.servers.invites.unit_of_work import ServerInviteUnitOfWork


class ServerInviteService(BaseService):
    def __init__(
        self,
        session: AsyncSession,
        server_invite_unit_of_work: ServerInviteUnitOfWork,
    ) -> None:
        super().__init__(session)
        self.uow = server_invite_unit_of_work

    def _generate_random_code(self, length: int = 8) -> str:
        """Generates a cryptographically secure random alphanumeric code.

        Args:
            length: The exact character length of the generated code. Defaults to 8.

        Returns:
            str: A random string containing uppercase/lowercase letters and digits.
        """
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(length))

    def _compute_validity_status(
        self, invite: ServerInvite
    ) -> Literal["valid", "expired", "exhausted"]:
        """Computes the current operational status of a server invite.

        The evaluation order adheres to strict precedence rules:
        1. Exhausted status takes priority if use limits are reached.
        2. Expired status is evaluated if the expiration timestamp has passed.
        3. Valid status is returned if neither condition is met.

        Args:
            invite: The invite schema object containing usage limits, usage counter,
                and expiration data.

        Returns:
            str: One of the following statuses: "exhausted", "expired", or "valid".
        """
        now = datetime.now(UTC)

        if invite.max_uses is not None and invite.use_count >= invite.max_uses:
            return "exhausted"

        if invite.expires_at is not None:
            expires_at = (
                invite.expires_at.replace(tzinfo=UTC)
                if invite.expires_at.tzinfo is None
                else invite.expires_at
            )
            if now > expires_at:
                return "expired"

        return "valid"

    async def create_invite(
        self, server_id: UUID, user_id: UUID, payload: CreateServerInviteRequest
    ) -> ServerInvite:
        """Creates a brand new unique invite code for a specific server.

        This action is restricted exclusively to the owner of the server. The method
        automatically handles potential database collisions by attempting to regenerate
        the code up to 3 times before failing.

        Args:
            server_id: The unique identifier of the target server.
            user_id: The unique identifier of the user requesting creation.
            payload: Request data containing configuration parameters such as 'expires_in'
                and 'max_uses'.

        Returns:
            ServerInviteOrm: The newly created database record instance.

        Raises:
            ServerInvitePermissionDeniedError: If the requesting user does not own the server.
            ServerInviteGenerationFailedError: If a unique code cannot be generated after
                3 consecutive collision attempts.
        """
        server = await self.uow.servers.get_one(id=server_id, owner_id=user_id)
        if not server:
            raise ServerInvitePermissionDeniedError

        expires_at = None
        if payload.expires_in is not None:
            expires_at = datetime.now(UTC) + timedelta(seconds=payload.expires_in)

        code = None
        for _ in range(3):
            potential_code = self._generate_random_code(8)
            exists = await self.uow.invites.get_one(code=potential_code)
            if not exists:
                code = potential_code
                break

        if not code:
            raise ServerInviteGenerationFailedError

        db_payload = CreateServerInvite(
            **payload.model_dump(),
            server_id=server_id,
            created_by=user_id,
            code=code,
            expires_at=expires_at,
        )

        invite = await self.uow.invites.create(db_payload)
        await self.uow.commit()
        return invite

    async def list_invites(
        self, user_id: UUID, server_id: UUID, limit: int = 100, offset: int = 0
    ) -> list[ServerInviteWithStatus]:
        """Retrieves a paginated list of all invites associated with a given server.

        Fetches records indiscriminately of their validity status, then maps each record
        to an output schema that appends a computed `validity_status` evaluation.

        Args:
            server_id: The unique identifier of the server whose invites are listed.
            limit: Maximum number of records to return. Defaults to 100.
            offset: The number of initial records to skip for pagination. Defaults to 0.

        Returns:
            list[ServerInviteSchema]: A list of enhanced response schemas including
                the calculated status for each invite.
        """
        server = await self.uow.servers.get_one(id=server_id, owner_id=user_id)
        if not server:
            return []

        invites = await self.uow.invites.get_filtered(
            server_id=server_id,
            limit=limit,
            offset=offset,
        )
        return [
            ServerInviteWithStatus(
                **invite.model_dump(),
                validity_status=self._compute_validity_status(invite),
            )
            for invite in invites
        ]

    async def delete_invite(self, server_id: UUID, user_id: UUID, code: str) -> None:
        """Deletes a specific invite from a server using its alphanumeric code.

        Ensures that only the server owner can initiate deletion, and safely restricts
        the query boundaries so that an invite cannot be deleted using a mismatched
        server context.

        Args:
            server_id: The unique identifier of the server context.
            user_id: The unique identifier of the executioner (must match server owner).
            code: The 8-character string token of the target invite.

        Returns:
            None

        Raises:
            ServerInviteCannotDeleteError: If the requester lacks administrative/owner
                permissions on the server.
            ServerInviteNotFoundError: If the code is absent or doesn't belong
                to this specific server.
        """
        server = await self.uow.servers.get_one(id=server_id, owner_id=user_id)
        if not server:
            raise ServerInviteCannotDeleteError

        invite = await self.uow.invites.get_one(server_id=server_id, code=code)

        if not invite:
            raise ServerInviteNotFoundError

        await self.uow.invites.delete(invite.id)
        await self.uow.commit()
