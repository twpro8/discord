// third party
import { createFileRoute } from "@tanstack/react-router";

// features
import HomePage from "@/pages/home/HomePage";

/** Home route rendering the main application page. */
export const Route = createFileRoute("/home")({
  component: HomePage,
});
