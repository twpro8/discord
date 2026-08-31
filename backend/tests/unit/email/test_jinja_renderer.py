from pathlib import Path

import pytest

from src.modules.email.adapters.rendering.jinja_renderer import (
    JinjaTemplateRenderer,
)
from src.modules.email.domain.enums import EmailTemplateName
from src.modules.email.domain.exceptions import (
    TemplateNotFoundError,
    TemplateRenderError,
)


async def test_renders_generic_notification_template() -> None:
    renderer = JinjaTemplateRenderer()

    rendered = await renderer.render(
        EmailTemplateName.GENERIC_NOTIFICATION,
        {"recipient_name": "Ada", "message": "Welcome aboard."},
    )

    assert "Ada" in rendered.subject
    assert "Ada" in rendered.html_body
    assert "Welcome aboard." in rendered.html_body
    assert rendered.text_body is not None
    assert "Welcome aboard." in rendered.text_body


async def test_html_body_escapes_context_but_text_body_does_not() -> None:
    renderer = JinjaTemplateRenderer()

    rendered = await renderer.render(
        EmailTemplateName.GENERIC_NOTIFICATION,
        {"recipient_name": "<b>Ada</b>", "message": "hi"},
    )

    assert "<b>Ada</b>" not in rendered.html_body
    assert "&lt;b&gt;Ada&lt;/b&gt;" in rendered.html_body
    assert rendered.text_body is not None
    assert "<b>Ada</b>" in rendered.text_body


async def test_missing_context_variable_raises_template_render_error() -> None:
    renderer = JinjaTemplateRenderer()

    with pytest.raises(TemplateRenderError):
        await renderer.render(EmailTemplateName.GENERIC_NOTIFICATION, {})


async def test_missing_template_directory_raises_template_not_found_error(
    tmp_path: Path,
) -> None:
    renderer = JinjaTemplateRenderer(templates_dir=tmp_path)

    with pytest.raises(TemplateNotFoundError):
        await renderer.render(
            EmailTemplateName.GENERIC_NOTIFICATION,
            {"recipient_name": "Ada", "message": "hi"},
        )
