import { createRootRoute, HeadContent, Outlet } from "@tanstack/react-router"
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools"
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { ServerRailProvider } from "@/context/ServerRailContext.tsx";
import { LayoutProvider } from "@/context/LayoutContext.tsx";

export const Route = createRootRoute({
    component: () => (
    <ServerRailProvider>
        <LayoutProvider>
            <HeadContent />
            <Outlet />
            <ReactQueryDevtools initialIsOpen={false} />
            <TanStackRouterDevtools position="bottom-right" />
        </LayoutProvider>
    </ServerRailProvider>
    ),
})
