import {
    createContext,
    useContext,
    useState,
    useCallback,
    type ReactNode,
} from "react";

export interface SidebarSlot {
    /** Arbitrary ReactNode to render inside the sidebar */
    content: ReactNode | null;
    /** Whether the sidebar is currently visible */
    visible: boolean;
}

interface LayoutContextValue {
    leftSidebar: SidebarSlot;
    rightSidebar: SidebarSlot;

    setLeftSidebar: (content: ReactNode | null) => void;
    setRightSidebar: (content: ReactNode | null) => void;

    toggleLeftSidebar: () => void;
    toggleRightSidebar: () => void;

    showLeftSidebar: () => void;
    hideLeftSidebar: () => void;
    showRightSidebar: () => void;
    hideRightSidebar: () => void;
}

const LayoutContext = createContext<LayoutContextValue | null>(null);

interface LayoutProviderProps {
    children: ReactNode;
}

export function LayoutProvider({ children }: LayoutProviderProps) {
    const [leftSidebar, setLeftState] = useState<SidebarSlot>({
        content: null,
        visible: true,
    });
    const [rightSidebar, setRightState] = useState<SidebarSlot>({
        content: null,
        visible: false,
    });

    const setLeftSidebar = useCallback((content: ReactNode | null) => {
        setLeftState((prev) => ({ ...prev, content, visible: content !== null }));
    }, []);

    const setRightSidebar = useCallback((content: ReactNode | null) => {
        setRightState((prev) => ({ ...prev, content, visible: content !== null }));
    }, []);

    const toggleLeftSidebar = useCallback(() => {
        setLeftState((prev) => ({ ...prev, visible: !prev.visible }));
    }, []);

    const toggleRightSidebar = useCallback(() => {
        setRightState((prev) => ({ ...prev, visible: !prev.visible }));
    }, []);

    const showLeftSidebar = useCallback(() => {
        setLeftState((prev) => ({ ...prev, visible: true }));
    }, []);

    const hideLeftSidebar = useCallback(() => {
        setLeftState((prev) => ({ ...prev, visible: false }));
    }, []);

    const showRightSidebar = useCallback(() => {
        setRightState((prev) => ({ ...prev, visible: true }));
    }, []);

    const hideRightSidebar = useCallback(() => {
        setRightState((prev) => ({ ...prev, visible: false }));
    }, []);

    return (
        <LayoutContext.Provider
            value={{
                leftSidebar,
                rightSidebar,
                setLeftSidebar,
                setRightSidebar,
                toggleLeftSidebar,
                toggleRightSidebar,
                showLeftSidebar,
                hideLeftSidebar,
                showRightSidebar,
                hideRightSidebar,
            }}
        >
            {children}
        </LayoutContext.Provider>
    );
}

export function useLayout() {
    const ctx = useContext(LayoutContext);

    if (!ctx) {
        throw new Error("useLayout must be used inside <LayoutProvider>");
    }

    return ctx;
}
