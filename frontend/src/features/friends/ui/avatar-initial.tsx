export function AvatarInitial({ username }: { username: string }) {
  return (
    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-semibold text-primary">
      {username.charAt(0).toUpperCase()}
    </div>
  )
}
