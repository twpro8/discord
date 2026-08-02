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
from src.modules.users.public.facade import MediatorUsersFacade
from src.shared.application.handler_registry import HandlerRegistry, RequestServices
from src.shared.application.mediator import Mediator


def _build_uow(services: RequestServices) -> ChatUnitOfWorkImpl:
    return ChatUnitOfWorkImpl(
        session=services.session,
        chat_repository=ChatRepositoryImpl(services.session),
        chat_member_repository=ChatMemberRepositoryImpl(services.session),
    )


def _build_create_chat_handler(
    services: RequestServices, _mediator: Mediator
) -> CreateChatCommandHandler:
    return CreateChatCommandHandler(_build_uow(services), services.event_bus)


def _build_update_chat_handler(
    services: RequestServices, _mediator: Mediator
) -> UpdateChatCommandHandler:
    return UpdateChatCommandHandler(_build_uow(services))


def _build_add_member_handler(
    services: RequestServices, mediator: Mediator
) -> AddMemberCommandHandler:
    return AddMemberCommandHandler(_build_uow(services), MediatorUsersFacade(mediator))


def _build_remove_member_handler(
    services: RequestServices, _mediator: Mediator
) -> RemoveMemberCommandHandler:
    return RemoveMemberCommandHandler(_build_uow(services))


def _build_leave_chat_handler(
    services: RequestServices, _mediator: Mediator
) -> LeaveChatCommandHandler:
    return LeaveChatCommandHandler(_build_uow(services))


def _build_mark_chat_as_read_handler(
    services: RequestServices, _mediator: Mediator
) -> MarkChatAsReadCommandHandler:
    return MarkChatAsReadCommandHandler(_build_uow(services))


def _build_get_chats_handler(
    services: RequestServices, _mediator: Mediator
) -> GetChatsQueryHandler:
    return GetChatsQueryHandler(ChatRepositoryImpl(services.session))


def _build_get_chat_details_handler(
    services: RequestServices, _mediator: Mediator
) -> GetChatDetailsQueryHandler:
    return GetChatDetailsQueryHandler(
        ChatRepositoryImpl(services.session), ChatMemberRepositoryImpl(services.session)
    )


def _build_list_members_handler(
    services: RequestServices, _mediator: Mediator
) -> ListMembersQueryHandler:
    return ListMembersQueryHandler(
        ChatRepositoryImpl(services.session), ChatMemberRepositoryImpl(services.session)
    )


def register_chat_handlers(registry: HandlerRegistry) -> None:
    registry.register_command_factory(CreateChatCommand, _build_create_chat_handler)
    registry.register_command_factory(UpdateChatCommand, _build_update_chat_handler)
    registry.register_command_factory(AddMemberCommand, _build_add_member_handler)
    registry.register_command_factory(RemoveMemberCommand, _build_remove_member_handler)
    registry.register_command_factory(LeaveChatCommand, _build_leave_chat_handler)
    registry.register_command_factory(
        MarkChatAsReadCommand, _build_mark_chat_as_read_handler
    )

    registry.register_query_factory(GetChatsQuery, _build_get_chats_handler)
    registry.register_query_factory(
        GetChatDetailsQuery, _build_get_chat_details_handler
    )
    registry.register_query_factory(ListMembersQuery, _build_list_members_handler)
