import { useState } from 'react'
import { UserPlus } from 'lucide-react'
import { AddFriendModal } from './AddFriendModal'

export function FriendPanel() {
  const [isAddFriendOpen, setIsAddFriendOpen] = useState(false)

  return (
    <aside className="flex h-screen w-80 flex-col border-l border-border bg-background/95 p-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-[0.2em] text-muted-foreground">Friends</h2>
        <button
          className="rounded-lg border border-border p-2 text-foreground"
          type="button"
          aria-label="Add friend"
          onClick={() => setIsAddFriendOpen(true)}
        >
          <UserPlus className="h-4 w-4" />
        </button>
      </div>

      <div className="mt-4 rounded-2xl border border-dashed border-border bg-muted/30 p-4 text-sm text-muted-foreground">
        Friend requests are ready for a future backend endpoint. The UI is wired so you can extend it easily.
      </div>

      <AddFriendModal open={isAddFriendOpen} onClose={() => setIsAddFriendOpen(false)} />
    </aside>
  )
}
