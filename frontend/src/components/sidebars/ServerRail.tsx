import { Mic, Headphones, Settings, Plus, MessageCircle } from "lucide-react";

import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { useServerRail } from "@/context/ServerRailContext";
import { Link } from "@tanstack/react-router";
import { ROUTES } from "@/routes.ts";
import type { UserServerSummarySchema } from "@/client";
import { colorFromId, getInitials } from "@/utils.ts";
import { ScrollArea } from "@/components/ui/scroll-area.tsx";

interface ServerIconProps {
    server: UserServerSummarySchema;
    active: boolean;
    onClick: () => void;
}

function ServerIcon({ server, active, onClick }: ServerIconProps) {
    return (
        <TooltipProvider delayDuration={200}>
            <Tooltip>
                <TooltipTrigger asChild>
                    <button
                        onClick={onClick}
                        aria-label={server.id}
                        aria-pressed={active}
                        className={`w-9 h-9 flex items-center justify-center font-semibold text-sm transition-all duration-150 cursor-pointer ${
                            active
                                ? "rounded-xl"
                                : "rounded-2xl hover:rounded-xl"
                        }`}
                        style={{
                            backgroundColor: colorFromId(server.id),
                            color: "var(--crust)",
                        }}
                    >
                        {getInitials(server.name)}
                    </button>
                </TooltipTrigger>
                <TooltipContent side="right">
                    <p>{server.name}</p>
                </TooltipContent>
            </Tooltip>
        </TooltipProvider>
    );
}

function ServerRailSeparator() {
    return (
        <div
            className="my-2 w-8 shrink-0"
            style={{
                height: 1,
                backgroundColor: "var(--surface1)",
            }}
        />
    )
}

export function ServerRail() {
    const { servers, activeServerId, setActiveServerId } = useServerRail();

    return (
        <aside
            className="flex flex-col items-center py-3 px-1.5 shrink-0 min-h-0 overflow-hidden"
            style={{ width: 56, height: "100vh", backgroundColor: "var(--crust)" }}
        >
            {/* DM button */}
            <Link
                className="w-9 h-9 rounded-full flex items-center justify-center shrink-0"
                style={{ backgroundColor: "var(--blue)", color: "var(--crust)" }}
                onClick={() => setActiveServerId(null)}
                to={ROUTES.CHATS}
            >
                <MessageCircle size={16} />
            </Link>

            <ServerRailSeparator />

            {/* List of servers */}
            <ScrollArea className="w-full shrink min-h-0">
                <div className="flex flex-col items-center gap-2 py-1">
                    {servers.map((server) => (
                        <ServerIcon
                            key={server.id}
                            server={server}
                            active={server.id === activeServerId}
                            onClick={() => setActiveServerId(server.id)}
                        />
                        ))}
                </div>
            </ScrollArea>

            <ServerRailSeparator />

            {/* Add a new server button */}
            <button
                className="w-9 h-9 rounded-full flex items-center justify-center transition-colors hover:rounded-xl shrink-0 cursor-pointer"
                style={{ backgroundColor: "var(--surface0)", color: "var(--green)" }}
                aria-label="Add server"
            >
                <Plus size={16} />
            </button>

            {/* User controls pinned to bottom */}
            <div className="mt-auto flex flex-col items-center gap-1">
                <button
                    className="p-1.5 rounded hover:bg-(--surface0) transition-colors"
                    style={{ color: "var(--overlay2)" }}
                    aria-label="Toggle microphone"
                >
                    <Mic size={14} />
                </button>
                <button
                    className="p-1.5 rounded hover:bg-(--surface0) transition-colors"
                    style={{ color: "var(--overlay2)" }}
                    aria-label="Toggle headphones"
                >
                    <Headphones size={14} />
                </button>
                <button
                    className="p-1.5 rounded hover:bg-(--surface0) transition-colors"
                    style={{ color: "var(--overlay2)" }}
                    aria-label="Settings"
                >
                    <Settings size={14} />
                </button>
            </div>
        </aside>
    );
}
