import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar } from "@/components/Avatar";
import { SERVER_MEMBERS } from "@/data";
import type { Member } from "@/types";

function MemberRow({ member }: { member: Member }) {
    return (
        <div className="flex items-center gap-2 px-2 py-1 rounded-md hover:bg-(--surface0) cursor-pointer transition-colors">
            <Avatar
                initials={member.initials}
                color={member.color}
                size="sm"
                status={member.status}
            />
            <span
                className="text-xs truncate"
                style={{
                    color: member.status === "online" ? "var(--text)" : "var(--overlay1)",
                }}
            >
        {member.name}
      </span>
        </div>
    );
}

export function MemberList() {
    const online = SERVER_MEMBERS.filter((m) => m.status === "online");
    const away   = SERVER_MEMBERS.filter((m) => m.status !== "online");

    return (
        <ScrollArea className="flex-1">
            <div className="px-3 pt-4 pb-2">
                <p
                    className="text-[10px] font-semibold tracking-wider mb-2 px-2"
                    style={{ color: "var(--overlay1)" }}
                >
                    MEMBERS
                </p>

                <p className="text-[11px] px-2 mb-1.5" style={{ color: "var(--green)" }}>
                    ● Online — {online.length}
                </p>
                <div className="space-y-0.5">
                    {online.map((m) => (
                        <MemberRow key={m.name} member={m} />
                    ))}
                </div>

                <p className="text-[11px] px-2 mt-3 mb-1.5" style={{ color: "var(--overlay2)" }}>
                    ○ Away — {away.length}
                </p>
                <div className="space-y-0.5">
                    {away.map((m) => (
                        <MemberRow key={m.name} member={m} />
                    ))}
                </div>
            </div>
        </ScrollArea>
    );
}
