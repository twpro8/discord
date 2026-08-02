from src.modules.auth.composition import register_auth_handlers
from src.modules.channels.composition import register_channel_handlers
from src.modules.chats.composition import register_chat_handlers
from src.modules.friends.composition import register_friend_handlers
from src.modules.messages.composition import register_message_handlers
from src.modules.servers.composition import register_server_handlers
from src.modules.users.composition import register_user_handlers
from src.shared.application.handler_registry import HandlerRegistry


def build_handler_registry() -> HandlerRegistry:
    """Builds the process-lifetime map of command/query type -> handler
    factory, called once from main.py's create_app() and stored on
    app.state.handler_registry.

    All 7 modules are registered here now (see AGENTS.md's DI lifetime
    model and shared/application/in_process_mediator.py's docstring for
    the full history) -- InProcessMediator's eager register_command/
    register_query path they migrated off of is no longer reachable from
    get_mediator, but still exists pending its removal as a follow-up
    cleanup.
    """
    registry = HandlerRegistry()
    register_channel_handlers(registry)
    register_user_handlers(registry)
    register_friend_handlers(registry)
    register_chat_handlers(registry)
    register_server_handlers(registry)
    register_message_handlers(registry)
    register_auth_handlers(registry)
    return registry
