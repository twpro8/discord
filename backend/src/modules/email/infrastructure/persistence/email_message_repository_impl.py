from dataclasses import asdict
from datetime import UTC, datetime
from uuid import UUID

from asyncpg.exceptions import UniqueViolationError
from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.email.domain.entities.dtos import EmailMessageCreate
from src.modules.email.domain.entities.email_message import EmailMessage
from src.modules.email.domain.enums import EmailStatus
from src.modules.email.infrastructure.persistence.mappers import EmailMessageDataMapper
from src.modules.email.infrastructure.persistence.models import EmailMessageOrm


class EmailMessageRepositoryImpl:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, data: EmailMessageCreate) -> EmailMessage:
        """Create-or-get: a concurrent caller racing on the same
        `idempotency_key` hits the table's unique index rather than a
        Python-level check-then-act gap — caught here and treated as
        "already scheduled" instead of a hard failure, per the module's
        duplicate-sending-prevention design."""
        stmt = insert(EmailMessageOrm).values(**asdict(data)).returning(EmailMessageOrm)
        try:
            result = await self._session.execute(stmt)
        except IntegrityError as e:
            cause = getattr(e.orig, "__cause__", None)
            if data.idempotency_key is not None and isinstance(
                cause, UniqueViolationError
            ):
                await self._session.rollback()
                existing = await self.find_by_idempotency_key(data.idempotency_key)
                if existing is not None:
                    return existing
            raise
        return EmailMessageDataMapper.to_entity(result.scalar_one())

    async def find_by_id(self, message_id: UUID) -> EmailMessage | None:
        query = select(EmailMessageOrm).filter_by(id=message_id)
        result = await self._session.execute(query)
        model = result.scalar_one_or_none()
        return EmailMessageDataMapper.to_entity(model) if model else None

    async def find_by_idempotency_key(
        self, idempotency_key: str
    ) -> EmailMessage | None:
        query = select(EmailMessageOrm).filter_by(idempotency_key=idempotency_key)
        result = await self._session.execute(query)
        model = result.scalar_one_or_none()
        return EmailMessageDataMapper.to_entity(model) if model else None

    async def mark_sent(
        self, message_id: UUID, *, provider_message_id: str | None
    ) -> EmailMessage:
        stmt = (
            update(EmailMessageOrm)
            .where(EmailMessageOrm.id == message_id)
            .values(
                status=EmailStatus.SENT,
                attempts=EmailMessageOrm.attempts + 1,
                provider_message_id=provider_message_id,
                error_message=None,
                sent_at=datetime.now(UTC),
            )
            .returning(EmailMessageOrm)
        )
        result = await self._session.execute(stmt)
        return EmailMessageDataMapper.to_entity(result.scalar_one())

    async def mark_retrying(self, message_id: UUID, *, error: str) -> EmailMessage:
        stmt = (
            update(EmailMessageOrm)
            .where(EmailMessageOrm.id == message_id)
            .values(
                status=EmailStatus.RETRYING,
                attempts=EmailMessageOrm.attempts + 1,
                error_message=error,
            )
            .returning(EmailMessageOrm)
        )
        result = await self._session.execute(stmt)
        return EmailMessageDataMapper.to_entity(result.scalar_one())

    async def mark_failed(self, message_id: UUID, *, error: str) -> EmailMessage:
        stmt = (
            update(EmailMessageOrm)
            .where(EmailMessageOrm.id == message_id)
            .values(
                status=EmailStatus.FAILED,
                attempts=EmailMessageOrm.attempts + 1,
                error_message=error,
            )
            .returning(EmailMessageOrm)
        )
        result = await self._session.execute(stmt)
        return EmailMessageDataMapper.to_entity(result.scalar_one())
