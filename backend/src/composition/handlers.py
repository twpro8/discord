from src.modules.channels.composition import register_channel_handlers
from src.shared.application.handler_registry import HandlerRegistry


def build_handler_registry() -> HandlerRegistry:
    """Builds the process-lifetime map of command/query type -> handler
    factory, called once from main.py's create_app() and stored on
    app.state.handler_registry.

    Modules register their factories here one at a time as they migrate
    off the legacy eager-registration path in their own composition.py
    (see AGENTS.md's DI lifetime model and
    shared/application/in_process_mediator.py's docstring). Modules not
    yet migrated are still registered eagerly, per-request, directly in
    api/v1/dependencies.py::get_mediator.
    """
    registry = HandlerRegistry()
    register_channel_handlers(registry)
    return registry
