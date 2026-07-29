from contextlib import AsyncExitStack

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.chats.application.commands.create_chat import (
    CreateChatCommand,
    CreateChatCommandHandler,
)
from src.modules.chats.application.queries.get_chats import (
    GetChatsQuery,
    GetChatsQueryHandler,
)
from src.modules.chats.infrastructure.chat_unit_of_work_impl import ChatUnitOfWorkImpl
from src.modules.chats.infrastructure.persistence.chat_member_repository_impl import (
    ChatMemberRepositoryImpl,
)
from src.modules.chats.infrastructure.persistence.chat_repository_impl import (
    ChatRepositoryImpl,
)
from src.shared.application.in_process_mediator import InProcessMediator


async def register_chat_handlers(
    mediator: InProcessMediator,
    session: AsyncSession,
    stack: AsyncExitStack,
) -> None:
    chat_repository = ChatRepositoryImpl(session)
    chat_member_repository = ChatMemberRepositoryImpl(session)
    uow = await stack.enter_async_context(
        ChatUnitOfWorkImpl(
            session=session,
            chat_repository=chat_repository,
            chat_member_repository=chat_member_repository,
        )
    )

    mediator.register_command(CreateChatCommand, CreateChatCommandHandler(uow))
    mediator.register_query(GetChatsQuery, GetChatsQueryHandler(chat_repository))
