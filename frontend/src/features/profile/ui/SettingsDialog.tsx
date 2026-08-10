// react
import { useState } from "react";

// shared
import { cn } from "@/shared/helpers/utils";
import { Modal } from "@/shared/ui/modal";

import { ThemeForm } from "@/features/theme/ui/ThemeForm";

// relative
import { PasswordForm } from "./PasswordForm";
import { ProfileForm } from "./ProfileForm";

type SettingsTab = "profile" | "appearance" | "password";

/** Modal for editing the current user's profile, appearance, and password. */
export function SettingsDialog({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const [tab, setTab] = useState<SettingsTab>("profile");

  return (
    <Modal
      open={open}
      onClose={onClose}
      className="max-h-[calc(100dvh-2rem)] w-[calc(100%-2rem)] max-w-4xl gap-0 overflow-hidden p-0 sm:max-w-4xl"
    >
      <div className="flex min-h-0 flex-col">
        <div className="flex shrink-0 gap-1 bg-muted p-2 pr-10">
          <TabButton
            active={tab === "profile"}
            onClick={() => setTab("profile")}
          >
            Profile
          </TabButton>
          <TabButton
            active={tab === "appearance"}
            onClick={() => setTab("appearance")}
          >
            Appearance
          </TabButton>
          <TabButton
            active={tab === "password"}
            onClick={() => setTab("password")}
          >
            Password
          </TabButton>
        </div>
        <div className="min-h-0 overflow-y-auto p-4">
          {tab === "profile" ? (
            <ProfileForm />
          ) : tab === "appearance" ? (
            <ThemeForm />
          ) : (
            <PasswordForm />
          )}
        </div>
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
