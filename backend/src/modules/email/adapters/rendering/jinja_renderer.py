from collections.abc import Mapping
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateNotFound
from jinja2 import UndefinedError as Jinja2UndefinedError

from src.modules.email.domain.entities.dtos import RenderedEmailContent
from src.modules.email.domain.enums import EmailTemplateName
from src.modules.email.domain.exceptions import (
    TemplateNotFoundError,
    TemplateRenderError,
)

_DEFAULT_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


class JinjaTemplateRenderer:
    """The only place Jinja2 mechanics live — `domain`/`application` only
    ever see the `TemplateRenderer` port and its `RenderedEmailContent`
    return value.

    Autoescaping is scoped to `*.html.jinja` files only (via a callable
    `autoescape`, since these templates live under a shared `.jinja`
    extension that Jinja2's built-in `select_autoescape` can't
    distinguish by suffix alone) — the plain-text/subject templates must
    NOT be HTML-escaped.
    """

    def __init__(self, templates_dir: Path = _DEFAULT_TEMPLATES_DIR) -> None:
        self._env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=lambda name: name is not None and name.endswith(".html.jinja"),
            undefined=StrictUndefined,
        )

    async def render(
        self,
        template: EmailTemplateName,
        context: Mapping[str, Any],
    ) -> RenderedEmailContent:
        try:
            subject_template = self._env.get_template(f"{template.value}/subject.jinja")
            html_template = self._env.get_template(f"{template.value}/body.html.jinja")
        except TemplateNotFound as exc:
            raise TemplateNotFoundError(template.value) from exc

        text_template = None
        try:
            text_template = self._env.get_template(f"{template.value}/body.txt.jinja")
        except TemplateNotFound:
            pass

        try:
            subject = subject_template.render(context).strip()
            html_body = html_template.render(context)
            text_body = text_template.render(context) if text_template else None
        except Jinja2UndefinedError as exc:
            raise TemplateRenderError(str(exc)) from exc

        return RenderedEmailContent(
            subject=subject,
            html_body=html_body,
            text_body=text_body,
        )
