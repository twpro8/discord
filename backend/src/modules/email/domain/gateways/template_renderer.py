from collections.abc import Mapping
from typing import Any, Protocol

from src.modules.email.domain.entities.dtos import RenderedEmailContent
from src.modules.email.domain.enums import EmailTemplateName


class TemplateRenderer(Protocol):
    """Port for turning a template name + context into subject/body content.
    Implemented by `infrastructure/rendering/jinja_renderer.py::JinjaTemplateRenderer`
    — the application layer never touches Jinja2 directly."""

    async def render(
        self,
        template: EmailTemplateName,
        context: Mapping[str, Any],
    ) -> RenderedEmailContent: ...
