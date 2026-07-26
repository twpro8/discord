// third party
import { createFileRoute } from "@tanstack/react-router";

// features
import RegisterPage from "@/pages/register/RegisterPage";

/** Register route rendering the registration page. */
export const Route = createFileRoute("/register")({
  component: RegisterPage,
});
