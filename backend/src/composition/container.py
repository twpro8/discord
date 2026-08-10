from dataclasses import dataclass, field

from fastapi import APIRouter

from src.modules.auth.module import register_auth_module
from src.modules.calls.module import register_calls_module
from src.modules.channels.module import register_channels_module
from src.modules.chats.module import register_chats_module
from src.modules.friends.module import register_friends_module
from src.modules.presence.module import register_presence_module
from src.modules.servers.module import register_servers_module
from src.modules.users.module import register_users_module


@dataclass
class Container:
    module_routers: list[APIRouter] = field(default_factory=list)


def build_container() -> Container:
    container = Container()

    auth_module = register_auth_module()
    users_router = register_users_module()
    friends_router = register_friends_module()
    servers_router = register_servers_module()
    channels_router = register_channels_module()
    chats_router = register_chats_module()
    presence_router = register_presence_module()
    calls_router = register_calls_module()

    container.module_routers.append(auth_module)
    container.module_routers.append(users_router)
    container.module_routers.append(friends_router)
    container.module_routers.append(servers_router)
    container.module_routers.append(channels_router)
    container.module_routers.append(chats_router)
    container.module_routers.append(presence_router)
    container.module_routers.append(calls_router)

    return container
