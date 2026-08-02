// third party
import { createRootRoute, Outlet } from "@tanstack/react-router";

/** Root layout rendering child routes via Outlet. */
export const Route = createRootRoute({
  component: Outlet,
});
