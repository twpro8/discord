// react
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

// third party
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createRouter, RouterProvider } from "@tanstack/react-router";

// relative
import "./index.css";

import { initializeTheme } from "./features/theme/model/theme";
import { ThemeProvider } from "./features/theme/ui/ThemeProvider";
import { routeTree } from "./routeTree.gen";
import { SonnerProvider } from "./shared/ui/sonner-provider";

const queryClient = new QueryClient();
const router = createRouter({ routeTree });

initializeTheme();

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <SonnerProvider />
        <RouterProvider router={router} />
      </ThemeProvider>
    </QueryClientProvider>
  </StrictMode>,
);
