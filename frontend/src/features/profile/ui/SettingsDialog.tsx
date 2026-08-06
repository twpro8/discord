// react
import { useState } from "react";

// shared
import { cn } from "@/shared/helpers/utils";
import { Modal } from "@/shared/ui/modal";

// relative
import { PasswordForm } from "./PasswordForm";
import { ProfileForm } from "./ProfileForm";

type SettingsTab = "profile" | "password";

/** Modal for editing the current user's profile and password. */
export function SettingsDialog({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const [tab, setTab] = useState<SettingsTab>("profile");

  return (
    <Modal open={open} onClose={onClose}>
      <div className="flex gap-1 rounded-lg bg-muted p-1">
        <TabButton active={tab === "profile"} onClick={() => setTab("profile")}>
          Profile
        </TabButton>
        <TabButton
          active={tab === "password"}
          onClick={() => setTab("password")}
        >
          Password
        </TabButton>
      </div>
      <div className="pt-1">
        {tab === "profile" ? <ProfileForm /> : <PasswordForm />}
      </div>
    </Modal>
  );
}

function TabButton({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "flex-1 rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
        active
          ? "bg-background text-foreground shadow-sm"
          : "text-muted-foreground hover:text-foreground",
      )}
    >
      {children}
    </button>
  );
}
