import type { UserStatus } from "@/types";

type AvatarSize = "sm" | "md" | "lg";

interface AvatarProps {
    initials: string;
    color: string;
    size?: AvatarSize;
    status?: UserStatus;
}

const SIZE_CLASSES: Record<AvatarSize, string> = {
    sm: "w-7 h-7 text-[10px]",
    md: "w-9 h-9 text-xs",
    lg: "w-10 h-10 text-sm",
};

const STATUS_COLORS: Record<UserStatus, string> = {
    online:  "var(--green)",
    away:    "var(--yellow)",
    offline: "var(--overlay2)",
};

export function Avatar({ initials, color, size = "md", status }: AvatarProps) {
    return (
        <div className="relative shrink-0">
            <div
                className={`${SIZE_CLASSES[size]} rounded-full flex items-center justify-center font-semibold`}
                style={{ backgroundColor: color, color: "var(--base)", opacity: 0.85 }}>
                {initials}
            </div>

            {status && (
                <span
                    className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full border-2"
                    style={{
                        backgroundColor: STATUS_COLORS[status],
                        borderColor: "var(--mantle)",
                    }}
                />
            )}
        </div>
    );
}
