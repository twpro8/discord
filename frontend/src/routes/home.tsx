// third party
import { createFileRoute } from "@tanstack/react-router";

// features
import HomeLayout from "@/pages/home/HomeLayout";

/** Home layout rendering the authenticated application shell. */
export const Route = createFileRoute("/home")({
  component: HomeLayout,
});
