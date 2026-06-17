import { useLayout } from "@/context/LayoutContext";

/**
 * LeftSidebar renders whatever content the current route injects via
 * `useLayout().setLeftSidebar(...)`. Nothing page-specific lives here.
 */
export function LeftSidebar() {
    const { leftSidebar } = useLayout();

    if (!leftSidebar.visible || !leftSidebar.content) return null;

    return (
        <aside
            className="flex flex-col h-full min-h-0 shrink-0 overflow-hidden"
            style={{ width: 220, backgroundColor: "var(--mantle)" }}
            aria-label="Navigation"
        >
            {leftSidebar.content}
        </aside>
    );
}
