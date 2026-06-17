import { createFileRoute } from '@tanstack/react-router'
import ServerPage from "@/pages/ServerPage.tsx";

export const Route = createFileRoute('/_layout/servers')({
  component: () => <ServerPage />,
})
