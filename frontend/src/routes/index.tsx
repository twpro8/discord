// third party
import { createFileRoute, redirect } from "@tanstack/react-router";

// shared
import { checkAuth } from "@/shared/helpers/auth";

/** Root redirect: authenticated users go to /home, others to /login. */
export const Route = createFileRoute("/")({
  beforeLoad: async () => {
    const authenticated = await checkAuth();

    if (authenticated) {
      throw redirect({ to: "/home" });
    }

    throw redirect({ to: "/login" });
  },
});
