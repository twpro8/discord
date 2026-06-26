import {
    createContext,
    useContext,
    useState,
    useCallback,
    type ReactNode,
} from "react";
import { useNavigate } from "@tanstack/react-router";
import { ROUTES } from "@/routes.ts";
import { useQuery } from "@tanstack/react-query";
import { serversGetMyServersOptions } from "@/client/@tanstack/react-query.gen.ts";
import type {UserServerSummarySchema} from "@/client";

interface ServerRailContextValue {
    servers: UserServerSummarySchema[];
    activeServerId: string | null;
    activeServer: UserServerSummarySchema | undefined;
    setActiveServerId: (id: string | null) => void;
}

const ServerRailContext = createContext<ServerRailContextValue | null>(null);

export function ServerRailProvider({ children }: { children: ReactNode }) {
    const navigate = useNavigate();
    const [activeServerId, setActiveServerIdState] = useState<string | null>(null);

    const { data: servers = [] } = useQuery({
        ...serversGetMyServersOptions(),
        enabled: !!localStorage.getItem("access_token"),
    })

    const setActiveServerId = useCallback((id: string | null) => {
        setActiveServerIdState(id);
        if (id) {
            // todo: navigate({ to: "/server/$serverId", params: { serverId: id } })
            navigate({ to: ROUTES.SERVERS });
        }
    }, [navigate]);

    const activeServer = servers.find((s) => s.id === activeServerId);

    return (
        <ServerRailContext.Provider
            value={{ servers, activeServerId, activeServer, setActiveServerId }}
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
