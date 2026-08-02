from src.modules.friends.application.commands.accept_request import (
    AcceptFriendRequestCommand,
    AcceptFriendRequestCommandHandler,
)
from src.modules.friends.application.commands.delete_request import (
    DeleteFriendRequestCommand,
    DeleteFriendRequestCommandHandler,
)
from src.modules.friends.application.commands.remove_friend import (
    RemoveFriendCommand,
    RemoveFriendCommandHandler,
)
from src.modules.friends.application.commands.send_request import (
    SendFriendRequestCommand,
    SendFriendRequestCommandHandler,
)
from src.modules.friends.application.queries.get_friends import (
    GetFriendsQuery,
    GetFriendsQueryHandler,
)
from src.modules.friends.application.queries.get_requests import (
    GetFriendRequestsQuery,
    GetFriendRequestsQueryHandler,
)
from src.modules.friends.application.queries.get_sent_requests import (
    GetSentFriendRequestsQuery,
    GetSentFriendRequestsQueryHandler,
)
from src.modules.friends.infrastructure.friend_unit_of_work_impl import (
    FriendUnitOfWorkImpl,
)
from src.modules.friends.infrastructure.persistence.friend_repository_impl import (
    FriendRepositoryImpl,
)
from src.modules.users.public.facade import MediatorUsersFacade
from src.shared.application.handler_registry import HandlerRegistry, RequestServices
from src.shared.application.mediator import Mediator


def _build_uow(services: RequestServices) -> FriendUnitOfWorkImpl:
    return FriendUnitOfWorkImpl(
        services.session, FriendRepositoryImpl(services.session)
    )


def _build_send_request_handler(
    services: RequestServices, mediator: Mediator
) -> SendFriendRequestCommandHandler:
    return SendFriendRequestCommandHandler(
        _build_uow(services), MediatorUsersFacade(mediator)
    )


def _build_accept_request_handler(
    services: RequestServices, _mediator: Mediator
) -> AcceptFriendRequestCommandHandler:
    return AcceptFriendRequestCommandHandler(_build_uow(services))


def _build_delete_request_handler(
    services: RequestServices, _mediator: Mediator
) -> DeleteFriendRequestCommandHandler:
    return DeleteFriendRequestCommandHandler(_build_uow(services))


def _build_remove_friend_handler(
    services: RequestServices, _mediator: Mediator
) -> RemoveFriendCommandHandler:
    return RemoveFriendCommandHandler(_build_uow(services))


def _build_get_friends_handler(
    services: RequestServices, _mediator: Mediator
) -> GetFriendsQueryHandler:
    return GetFriendsQueryHandler(FriendRepositoryImpl(services.session))


def _build_get_friend_requests_handler(
    services: RequestServices, _mediator: Mediator
) -> GetFriendRequestsQueryHandler:
    return GetFriendRequestsQueryHandler(FriendRepositoryImpl(services.session))


def _build_get_sent_friend_requests_handler(
    services: RequestServices, _mediator: Mediator
) -> GetSentFriendRequestsQueryHandler:
    return GetSentFriendRequestsQueryHandler(FriendRepositoryImpl(services.session))


def register_friend_handlers(registry: HandlerRegistry) -> None:
    registry.register_command_factory(
        SendFriendRequestCommand, _build_send_request_handler
    )
    registry.register_command_factory(
        AcceptFriendRequestCommand, _build_accept_request_handler
    )
    registry.register_command_factory(
        DeleteFriendRequestCommand, _build_delete_request_handler
    )
    registry.register_command_factory(RemoveFriendCommand, _build_remove_friend_handler)
    registry.register_query_factory(GetFriendsQuery, _build_get_friends_handler)
    registry.register_query_factory(
        GetFriendRequestsQuery, _build_get_friend_requests_handler
    )
    registry.register_query_factory(
        GetSentFriendRequestsQuery, _build_get_sent_friend_requests_handler
    )
