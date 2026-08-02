from dataclasses import dataclass, field

from fastapi import APIRouter

from src.modules.auth.composition import register_auth_handlers
from src.modules.auth.module import register_auth_module
from src.modules.channels.composition import register_channel_handlers
from src.modules.channels.module import register_channels_module
from src.modules.chats.composition import register_chat_handlers
from src.modules.chats.module import register_chats_module
from src.modules.friends.composition import register_friend_handlers
from src.modules.friends.module import register_friends_module
from src.modules.messages.composition import register_message_handlers
from src.modules.servers.composition import register_server_handlers
from src.modules.servers.module import register_servers_module
from src.modules.users.composition import register_user_handlers
from src.modules.users.module import register_users_module
from src.shared.application.handler_registry import HandlerRegistry


@dataclass
class Container:
    """The composition root: the single explicit place the whole
    application gets wired together, built once at startup
    (main.py::create_app()) and stored on app.state.container.

    Holds both HTTP routers (module_routers, mounted by
    api/v1/router.py::build_api_v1_router) and the command/query handler
    factory map (handler_registry, resolved lazily per-dispatch by
    InProcessMediator -- see shared/application/handler_registry.py).
    """

    module_routers: list[APIRouter] = field(default_factory=list)
    handler_registry: HandlerRegistry = field(default_factory=HandlerRegistry)


def build_container() -> Container:
    container = Container()

    auth_module = register_auth_module()
    users_router = register_users_module()
    friends_router = register_friends_module()
    servers_router = register_servers_module()
    channels_router = register_channels_module()
    chats_router = register_chats_module()

    container.module_routers.append(auth_module)
    container.module_routers.append(users_router)
    container.module_routers.append(friends_router)
    container.module_routers.append(servers_router)
    container.module_routers.append(channels_router)
    container.module_routers.append(chats_router)

    register_channel_handlers(container.handler_registry)
    register_user_handlers(container.handler_registry)
    register_friend_handlers(container.handler_registry)
    register_chat_handlers(container.handler_registry)
    register_server_handlers(container.handler_registry)
    register_message_handlers(container.handler_registry)
    register_auth_handlers(container.handler_registry)

    return container
