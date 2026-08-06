// react
import { useState } from "react";

// shared
import { Avatar } from "@/shared/ui/avatar";
import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";
import { Label } from "@/shared/ui/label";

// relative
import { useCurrentUser } from "../model/use-current-user";
import { useUpdateAvatar } from "../model/use-update-avatar";
import { useUpdateProfile } from "../model/use-update-profile";

const AVATAR_ACCEPT = "image/jpeg,image/png,image/webp";

/** Edits the current user's name, username, email, and avatar. */
export function ProfileForm() {
  const { data: user } = useCurrentUser();
  const updateProfile = useUpdateProfile();
  const updateAvatar = useUpdateAvatar();

  const [name, setName] = useState(user?.name ?? "");
  const [username, setUsername] = useState(user?.username ?? "");
  const [email, setEmail] = useState(user?.email ?? "");
  const [avatarFile, setAvatarFile] = useState<File | null>(null);

  const avatarPreview = avatarFile
    ? URL.createObjectURL(avatarFile)
    : (user?.avatar_url ?? null);

  const isPending = updateProfile.isPending || updateAvatar.isPending;

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (avatarFile) {
      await updateAvatar.mutateAsync(avatarFile);
      setAvatarFile(null);
    }
    await updateProfile.mutateAsync({ name, username, email });
  }

  return (
    <form onSubmit={handleSubmit} className="grid gap-4">
      <div className="flex items-center gap-4">
        <Avatar
          name={user?.name ?? "U"}
          src={avatarPreview}
          className="h-16 w-16 text-xl"
        />
        <div className="flex flex-col gap-2">
          <Label htmlFor="avatar" className="w-fit cursor-pointer">
            <span className="rounded-lg bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground transition-colors hover:bg-primary/80">
              {avatarFile ? "Change image" : "Upload image"}
            </span>
          </Label>
          <input
            id="avatar"
            type="file"
            accept={AVATAR_ACCEPT}
            className="hidden"
            onChange={(event) => setAvatarFile(event.target.files?.[0] ?? null)}
          />
          <p className="text-xs text-muted-foreground">
            PNG, JPEG, or WebP, up to 5 MB.
          </p>
        </div>
      </div>

      <div className="grid gap-2">
        <Label htmlFor="settings-name">Display name</Label>
        <Input
          id="settings-name"
          value={name}
          onChange={(event) => setName(event.target.value)}
          maxLength={64}
        />
      </div>

      <div className="grid gap-2">
        <Label htmlFor="settings-username">Username</Label>
        <Input
          id="settings-username"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          minLength={3}
          maxLength={32}
        />
      </div>

      <div className="grid gap-2">
        <Label htmlFor="settings-email">Email</Label>
        <Input
          id="settings-email"
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          maxLength={32}
        />
      </div>

      <Button type="submit" disabled={isPending}>
        {isPending ? "Saving…" : "Save"}
      </Button>
    </form>
  );
}
