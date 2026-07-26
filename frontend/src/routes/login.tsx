// third party
import { createFileRoute } from "@tanstack/react-router";

// features
import LoginPage from "@/pages/login/LoginPage";

/** Login route rendering the login page. */
export const Route = createFileRoute("/login")({
  component: LoginPage,
});
