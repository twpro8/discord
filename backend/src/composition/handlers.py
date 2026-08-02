from src.shared.application.handler_registry import HandlerRegistry


def build_handler_registry() -> HandlerRegistry:
    """Builds the process-lifetime map of command/query type -> handler
    factory, called once from main.py's create_app() and stored on
    app.state.handler_registry.

    Empty for now: modules register their factories here one at a time as
    they migrate off the legacy eager-registration path in their own
    composition.py (see AGENTS.md's DI lifetime model and
    shared/application/in_process_mediator.py's docstring). Nothing is
    wired into this yet.
    """
    return HandlerRegistry()
