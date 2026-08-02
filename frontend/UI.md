# Lumiere UI direction

Lumiere should feel calm, focused, and dependable: a communication tool rather
than a social feed. The visual language is deliberately quiet, with a near-black
graphite foundation, soft surface separation, readable typography, and one
expressive colour used only to clarify actions and state.

## Principles

- **Content first.** Messages, names, and active conversations carry the visual
  hierarchy; decoration never competes with them.
- **Depth through tone, not heavy shadows.** Use adjacent surface colours and
  thin borders before introducing elevation.
- **One clear action.** A screen should have one primary action. Everything else
  is neutral or a subtle outline action.
- **Comfortable density.** Chat can be information-dense without becoming
  cramped. Keep targets at least 40px high and preserve whitespace between
  distinct groups.
- **Accessible by default.** Never communicate meaning using colour alone; every
  interactive state needs a visible keyboard focus treatment.

## Design tokens

Use semantic tokens in components (`--color-text-primary`), not raw colour
values. The palette below is the source of truth. Tailwind theme values, if
added, should reference the same CSS variables.

### Dark theme (default)

```css
:root {
  --color-canvas: #111318;
  --color-surface: #181b22;
  --color-surface-raised: #20242d;
  --color-surface-hover: #292e39;
  --color-border: #2b303a;
  --color-border-strong: #414858;

  --color-text-primary: #f3f5f7;
  --color-text-secondary: #aab1bf;
  --color-text-tertiary: #737b8b;
  --color-text-disabled: #555d6b;

  --color-accent: #7c8cff;
  --color-accent-hover: #93a0ff;
  --color-accent-pressed: #6575ed;
  --color-accent-subtle: #20264a;
  --color-on-accent: #ffffff;

  --color-success: #4ecb8d;
  --color-warning: #eab85d;
  --color-danger: #f17878;
  --color-info: #6eaeff;

  --color-overlay: rgb(5 7 11 / 64%);
  --shadow-raised: 0 8px 24px rgb(0 0 0 / 20%);
  --focus-ring: 0 0 0 3px rgb(124 140 255 / 35%);
}
```

### Light theme

Light mode is a warm off-white rather than pure white, retaining the same calm
contrast and indigo identity.

```css
[data-theme='light'] {
  --color-canvas: #f7f8fa;
  --color-surface: #ffffff;
  --color-surface-raised: #ffffff;
  --color-surface-hover: #eef0f5;
  --color-border: #e1e4ea;
  --color-border-strong: #c9cfda;

  --color-text-primary: #1b1f27;
  --color-text-secondary: #5d6573;
  --color-text-tertiary: #858c99;
  --color-text-disabled: #b0b5be;

  --color-accent: #5265d9;
  --color-accent-hover: #4558cb;
  --color-accent-pressed: #3c4db5;
  --color-accent-subtle: #e9ecff;
  --color-on-accent: #ffffff;

  --color-overlay: rgb(20 25 35 / 40%);
  --shadow-raised: 0 8px 24px rgb(27 31 39 / 10%);
  --focus-ring: 0 0 0 3px rgb(82 101 217 / 25%);
}
```

## Typography

Use **Geist** (or `Inter` as a fallback) for the interface. It is neutral,
compact, and highly readable in dense conversation views. Use a system monospace
face only for code, IDs, timestamps in developer-facing contexts, and keyboard
shortcuts.

```css
--font-sans: 'Geist', 'Inter', ui-sans-serif, system-ui, sans-serif;
--font-mono: 'Geist Mono', ui-monospace, SFMono-Regular, Consolas, monospace;
```

| Style | Size / line height | Weight | Use |
| --- | --- | --- | --- |
| Display | 28px / 34px | 650 | Authentication and empty-state titles |
| Heading | 20px / 28px | 600 | Page and dialog titles |
| Section | 14px / 20px | 600 | Sidebar group labels, compact headings |
| Body | 14px / 20px | 400 | Messages and standard UI text |
| Body small | 13px / 18px | 400 | Supporting text, metadata |
| Label | 12px / 16px | 600 | Inputs and compact controls |
| Caption | 11px / 14px | 500 | Timestamps and secondary status |

Avoid text below 12px except for non-essential timestamps. Use sentence case;
reserve all caps for very short, secondary navigation labels only.

## Spacing, shape, and elevation

Use a 4px base spacing scale: `4, 8, 12, 16, 20, 24, 32, 40, 48`.

- Page padding: 24px desktop, 16px mobile.
- Sidebar padding: 12px; list-item horizontal padding: 10–12px.
- Message groups: 2px between related messages, 16px between authors or a clear
  time gap.
- Control height: 40px standard; 32px compact; 44px primary touch control.
- Radius: 6px for small controls, 8px for cards/inputs, 12px for dialogs; use
  `999px` only for avatars and status dots.
- Use `--shadow-raised` only for dialogs, menus, and floating composers. Cards
  generally use a border, not a shadow.

## Layout

The application shell is intentionally stable:

```text
server rail (72px) | context sidebar (240–280px) | conversation (fluid) | details (280px, optional)
```

- The conversation pane has a maximum readable content width of 880px, while
  still allowing its background and composer to span the available pane.
- Headers are 56px high with a bottom border.
- Sidebars use `--color-surface`; the active conversation uses
  `--color-accent-subtle` with primary text, never a saturated full-width fill.
- On narrow screens, show one contextual pane at a time; sidebars become
  overlays or route-level views rather than compressing the message column.

## Components

### Buttons

- **Primary:** accent fill, `--color-on-accent` text; use for submit, send, and
  confirm actions.
- **Secondary:** `--color-surface-raised` fill and standard border; use for
  alternate actions.
- **Ghost:** transparent; hover uses `--color-surface-hover`; use in toolbars
  and lists.
- **Destructive:** danger text on a subtle danger tint first. Use a solid danger
  fill only for irreversible confirmations.
- Disabled controls reduce contrast and do not expose pointer affordance. Do not
  rely on opacity alone when it would make labels illegible.

### Inputs and composer

Inputs have a surface-raised background, 1px border, 8px radius, and a 40px
minimum height. Focus changes the border to `--color-accent` and applies
`--focus-ring`. The message composer is a raised, rounded container with a
multiline field; attachments and send are icon buttons with explicit accessible
labels.

### Lists, messages, and avatars

- List rows are 40px minimum and use an 8px radius on hover/active states.
- Messages are not individual cards. Group adjacent messages from the same
  author; show avatar and name on the group’s first message only.
- Message text uses primary colour; timestamps and delivery indicators use
  tertiary text and become clearer on hover/focus.
- Avatars use 32px in lists and 36px in message groups. If no image is present,
  generate a muted, deterministic colour from the user ID and show initials.

### Dialogs, menus, and feedback

- Dialog width: 420px by default, 560px for forms requiring more space.
- Dialogs use surface-raised, 12px radius, border, and `--shadow-raised`.
- Menus use 8px padding and 36px rows; destructive choices are visually
  separated from neutral choices.
- Toasts are concise and actionable. Success is transient; errors remain until
  dismissed or corrected. Inline validation appears next to the affected field.

## Interaction states

Every interactive component supports default, hover, active, focus-visible,
disabled, and loading states.

```css
:focus-visible {
  outline: none;
  box-shadow: var(--focus-ring);
}
```

Keep transitions subtle: 120–160ms, `ease-out`, limited to colour, opacity, and
small transforms. Respect `prefers-reduced-motion`; never make motion necessary
to understand a state change.

## Icons and imagery

Use a single 20px outline icon set, with 16px icons in compact controls and 24px
only for empty states. Icons clarify an action; they do not replace an
accessible name. Avoid decorative gradients, large illustrations, and excessive
status badges. Empty states can use a small line icon, a direct explanation,
and one primary action.

## Accessibility checks

- Text contrast meets WCAG AA: 4.5:1 for body text and 3:1 for large text/UI
  boundaries.
- Keyboard navigation follows the visual order; dialogs trap focus and return it
  to the triggering control.
- Touch targets are at least 40 × 40px, ideally 44 × 44px for primary actions.
- Status colour is paired with text, icon, or shape.
- Never remove focus indicators or use placeholder text as the only label.

## Implementation conventions

- Build primitives from semantic tokens; do not introduce component-local hex
  values.
- Keep one source of truth for tokens in the global stylesheet and map them into
  Tailwind only when Tailwind is introduced.
- Use `data-theme="dark"` and `data-theme="light"` on the document root so the
  selected preference can be persisted. Default to the system preference on a
  first visit.
- Use CSS logical properties (`padding-inline`, `margin-block`) where practical
  to preserve future RTL support.
