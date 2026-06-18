import { createFileRoute } from "@tanstack/react-router"
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

export const Route = createFileRoute("/_layout/")({
    component: RootLayout,
})

function RootLayout() {
    return (
        <div className="flex h-screen w-screen items-center justify-center flex-col gap-2">
            <p>Don't click the button...</p>
            <Button
                onClick={() => {
                    toast.error("Happy? Nothing here...");
                }}
            >
                Show Toast
            </Button>
        </div>
    )
}
