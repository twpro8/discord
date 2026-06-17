import {
    createContext,
    useContext,
    useState,
    useCallback,
    type ReactNode,
} from "react";
import { useNavigate } from "@tanstack/react-router";
import { SERVERS } from "@/data";
import type { Server } from "@/types";
import {ROUTES} from "@/routes.ts";

interface ServerRailContextValue {
    servers: Server[];
    activeServerId: string | null;
    activeServer: Server | undefined;
    setActiveServerId: (id: string | null) => void;
}

const ServerRailContext = createContext<ServerRailContextValue | null>(null);

export function ServerRailProvider({ children }: { children: ReactNode }) {
    const navigate = useNavigate();
    const [activeServerId, setActiveServerIdState] = useState<string | null>(null);

    const setActiveServerId = useCallback((id: string | null) => {
        setActiveServerIdState(id);
        if (id) {
            // todo: navigate({ to: "/server/$serverId", params: { serverId: id } })
            navigate({ to: ROUTES.SERVERS });
        }
    }, [navigate]);

    const activeServer = SERVERS.find((s) => s.id === activeServerId);

    return (
        <ServerRailContext.Provider
            value={{ servers: SERVERS, activeServerId, activeServer, setActiveServerId }}
        >
            {children}
        </ServerRailContext.Provider>
    );
}

export function useServerRail() {
    const ctx = useContext(ServerRailContext);

    if (!ctx) {
        throw new Error("useServerRail must be used inside <ServerRailProvider>");
    }

    return ctx;
}
