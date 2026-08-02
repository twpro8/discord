from sqlalchemy.ext.asyncio import AsyncSession

from src.core.event_bus import EventBus
from src.modules.chats.application.commands.add_member import (
    AddMemberCommand,
    AddMemberCommandHandler,
)
from src.modules.chats.application.commands.create_chat import (
    CreateChatCommand,
    CreateChatCommandHandler,
)
from src.modules.chats.application.commands.leave_chat import (
    LeaveChatCommand,
    LeaveChatCommandHandler,
)
from src.modules.chats.application.commands.mark_chat_as_read import (
    MarkChatAsReadCommand,
    MarkChatAsReadCommandHandler,
)
from src.modules.chats.application.commands.remove_member import (
    RemoveMemberCommand,
    RemoveMemberCommandHandler,
)
from src.modules.chats.application.commands.update_chat import (
    UpdateChatCommand,
    UpdateChatCommandHandler,
)
from src.modules.chats.application.queries.get_chat_details import (
    GetChatDetailsQuery,
    GetChatDetailsQueryHandler,
)
from src.modules.chats.application.queries.get_chats import (
    GetChatsQuery,
    GetChatsQueryHandler,
)
from src.modules.chats.application.queries.list_members import (
    ListMembersQuery,
    ListMembersQueryHandler,
)
from src.modules.chats.infrastructure.chat_unit_of_work_impl import ChatUnitOfWorkImpl
from src.modules.chats.infrastructure.persistence.chat_member_repository_impl import (
    ChatMemberRepositoryImpl,
)
from src.modules.chats.infrastructure.persistence.chat_repository_impl import (
    ChatRepositoryImpl,
)
from src.modules.users.public.facade import UsersFacade
from src.shared.application.in_process_mediator import InProcessMediator


def register_chat_handlers(
    mediator: InProcessMediator,
    session: AsyncSession,
    event_bus: EventBus,
    users_facade: UsersFacade,
) -> None:
    chat_repository = ChatRepositoryImpl(session)
    chat_member_repository = ChatMemberRepositoryImpl(session)
    uow = ChatUnitOfWorkImpl(
        session=session,
        chat_repository=chat_repository,
        chat_member_repository=chat_member_repository,
    )

    mediator.register_command(
        CreateChatCommand, CreateChatCommandHandler(uow, event_bus)
    )
    mediator.register_command(UpdateChatCommand, UpdateChatCommandHandler(uow))
    mediator.register_command(
        AddMemberCommand, AddMemberCommandHandler(uow, users_facade)
    )
    mediator.register_command(RemoveMemberCommand, RemoveMemberCommandHandler(uow))
    mediator.register_command(LeaveChatCommand, LeaveChatCommandHandler(uow))
    mediator.register_command(MarkChatAsReadCommand, MarkChatAsReadCommandHandler(uow))

    mediator.register_query(GetChatsQuery, GetChatsQueryHandler(chat_repository))
    mediator.register_query(
        GetChatDetailsQuery,
        GetChatDetailsQueryHandler(chat_repository, chat_member_repository),
    )
    mediator.register_query(
        ListMembersQuery,
        ListMembersQueryHandler(chat_repository, chat_member_repository),
    )
