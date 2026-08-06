// shared
import { Avatar } from "@/shared/ui/avatar";

// relative
import { useCurrentUser } from "../model/use-current-user";

/** Displays the current user's profile information. */
export function ProfileCard() {
  const { data: user, isLoading, error } = useCurrentUser();

  if (isLoading) {
    return (
      <div className="w-full max-w-2xl rounded-2xl border border-border bg-background/80 p-8 shadow-sm">
        <div className="animate-pulse space-y-3">
          <div className="h-4 w-24 rounded bg-muted" />
          <div className="h-8 w-40 rounded bg-muted" />
          <div className="h-4 w-56 rounded bg-muted" />
        </div>
      </div>
    );
  }

  if (error || !user) {
    return (
      <div className="w-full max-w-2xl rounded-2xl border border-destructive/20 bg-background/80 p-8 shadow-sm">
        <p className="text-sm text-destructive">
          Unable to load your profile right now.
        </p>
      </div>
    );
  }

  return (
    <div className="w-full max-w-2xl rounded-2xl border border-border bg-background/80 p-8 shadow-sm">
      <div className="flex items-center gap-4">
        <Avatar
          name={user.name}
          src={user.avatar_url}
          className="h-14 w-14 text-xl"
        />
        <div>
          <p className="text-sm font-medium text-muted-foreground">
            Signed in as
          </p>
          <h1 className="text-2xl font-semibold text-foreground">
            {user.name}
          </h1>
        </div>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        <div className="rounded-xl border border-border bg-muted/40 p-4">
          <p className="text-sm text-muted-foreground">Username</p>
          <p className="mt-1 font-medium text-foreground">{user.username}</p>
        </div>
        <div className="rounded-xl border border-border bg-muted/40 p-4">
          <p className="text-sm text-muted-foreground">Email</p>
          <p className="mt-1 font-medium text-foreground">{user.email}</p>
        </div>
      </div>
    </div>
  );
}
