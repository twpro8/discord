import { Mic, Headphones, Settings, Plus, MessageCircle } from "lucide-react";

import { Separator } from "@/components/ui/separator";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { useServerRail } from "@/context/ServerRailContext";
import type { Server } from "@/types";
import { Link } from "@tanstack/react-router";
import { ROUTES } from "@/routes.ts";

interface ServerIconProps {
    server: Server;
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
                        className={`w-9 h-9 flex items-center justify-center font-semibold text-sm transition-all duration-150 ${
                            active
                                ? "rounded-xl"
                                : "rounded-2xl hover:rounded-xl"
                        }`}
                        style={{
                            backgroundColor: server.color,
                            color: "var(--crust)",
                        }}
                    >
                        {server.label}
                    </button>
                </TooltipTrigger>
                <TooltipContent side="right">
                    <p>{server.id.toUpperCase()}</p>
                </TooltipContent>
            </Tooltip>
        </TooltipProvider>
    );
}

export function ServerRail() {
    const { servers, activeServerId, setActiveServerId } = useServerRail();

    return (
        <aside
            className="flex flex-col items-center gap-2 py-3 px-1.5 shrink-0"
            style={{ width: 56, backgroundColor: "var(--crust)" }}
            aria-label="Servers"
        >
            {/* DM button */}
            <Link
                className="w-9 h-9 rounded-full flex items-center justify-center"
                style={{ backgroundColor: "var(--blue)", color: "var(--crust)" }}
                onClick={() => setActiveServerId("")}
                to={ROUTES.CHATS}
            >
                <MessageCircle size={16} />
            </Link>

            {/* List of servers */}
            {servers.map((server) => (
                <ServerIcon
                    key={server.id}
                    server={server}
                    active={server.id === activeServerId}
                    onClick={() => setActiveServerId(server.id)}
                />
            ))}

            <Separator className="my-1" style={{ backgroundColor: "var(--surface1)" }} />

            {/* Add a new server button */}
            <button
                className="w-9 h-9 rounded-full flex items-center justify-center transition-colors hover:rounded-xl"
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
