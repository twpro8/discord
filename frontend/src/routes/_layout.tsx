import { createFileRoute, Outlet } from "@tanstack/react-router"

import { ServerRail } from "@/components/sidebars/ServerRail.tsx";
import { LeftSidebar } from "@/components/sidebars/LeftSidebar.tsx";
import { RightSidebar } from "@/components/sidebars/RightSidebar.tsx";

export const Route = createFileRoute("/_layout")({
    component: () => (
        <div
            className="flex h-screen w-full overflow-hidden text-sm select-none"
            style={{ backgroundColor: "var(--base)", color: "var(--text)" }}
        >
            <ServerRail />
            <LeftSidebar />

            <main className="flex flex-col flex-1 min-w-0 overflow-hidden">
                <Outlet />
            </main>

            <RightSidebar />
        </div>
    ),
})
