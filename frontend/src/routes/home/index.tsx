// third party
import { createFileRoute } from "@tanstack/react-router";

// features
import HomeIndex from "@/pages/home/HomeIndex";

/** Default home content. */
export const Route = createFileRoute("/home/")({
  component: HomeIndex,
});
