import { createFileRoute, Outlet, redirect } from "@tanstack/react-router"
import { isLoggedIn } from "@/hooks/useAuth.tsx";
import { ROUTES } from "@/routes.ts";

export const Route = createFileRoute("/_layout")({
    component: () => <Outlet />,
    beforeLoad: () => {
        if (!isLoggedIn()) {
            throw redirect({ to: ROUTES.LOGIN })
        }
    },
})
