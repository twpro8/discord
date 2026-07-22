import { useLayout } from "@/context/LayoutContext";

/**
 * RightSidebar renders whatever content the current route injects via
 * `useLayout().setRightSidebar(...)`. Nothing page-specific lives here.
 */
export function RightSidebar() {
    const { rightSidebar } = useLayout();

    if (!rightSidebar.visible || !rightSidebar.content) return null;

    return (
        <aside
            className="flex flex-col shrink-0 overflow-hidden"
            style={{
                width: "var(--layout-right-sidebar-width)",
                backgroundColor: "var(--mantle)",
                borderLeft: "1px solid var(--surface1)",
            }}
            aria-label="Members"
        >
            {rightSidebar.content}
        </aside>
    );
}
