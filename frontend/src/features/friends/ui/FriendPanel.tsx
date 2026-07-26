import { useState } from 'react'
import { UserPlus } from 'lucide-react'
import { AddFriendModal } from './AddFriendModal'
import { useFriendRequests } from '../model/use-friend-requests'
import type { FriendRequestWithUser } from '../model/types'

type Tab = 'pending' | 'sent'

function timeAgo(dateString: string): string {
  const now = Date.now()
  const date = new Date(dateString).getTime()
  const diffMs = now - date
  const diffSec = Math.floor(diffMs / 1000)

  if (diffSec < 60) return 'just now'
  const diffMin = Math.floor(diffSec / 60)
  if (diffMin < 60) return `${diffMin}m ago`
  const diffHour = Math.floor(diffMin / 60)
  if (diffHour < 24) return `${diffHour}h ago`
  const diffDay = Math.floor(diffHour / 24)
  if (diffDay < 7) return `${diffDay}d ago`
  return new Date(dateString).toLocaleDateString()
}

function AvatarInitial({ username }: { username: string }) {
  return (
    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-semibold text-primary">
      {username.charAt(0).toUpperCase()}
    </div>
  )
}

function RequestItem({ request }: { request: FriendRequestWithUser }) {
  return (
    <div className="flex items-center gap-3 rounded-xl px-3 py-2.5 transition-colors hover:bg-muted/50">
      <AvatarInitial username={request.username} />
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium text-foreground">{request.username}</p>
        <p className="text-xs text-muted-foreground">{timeAgo(request.created_at)}</p>
      </div>
    </div>
  )
}

function Skeleton() {
  return (
    <div className="space-y-2 px-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="flex animate-pulse items-center gap-3 py-2.5">
          <div className="h-9 w-9 rounded-full bg-muted" />
          <div className="flex-1 space-y-1.5">
            <div className="h-3.5 w-20 rounded bg-muted" />
            <div className="h-3 w-14 rounded bg-muted" />
          </div>
        </div>
      ))}
    </div>
  )
}

function EmptyState({ label }: { label: string }) {
  return (
    <p className="px-3 pt-6 text-center text-sm text-muted-foreground">{label}</p>
  )
}

export function FriendPanel() {
  const [isAddFriendOpen, setIsAddFriendOpen] = useState(false)
  const [activeTab, setActiveTab] = useState<Tab>('pending')
  const { incoming, sent, isLoading } = useFriendRequests()

  const items = activeTab === 'pending' ? incoming : sent
  const emptyLabel = activeTab === 'pending' ? 'No pending requests' : 'No sent requests'

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

      <div className="mt-4 flex gap-1 rounded-lg bg-muted/50 p-0.5">
        <button
          type="button"
          onClick={() => setActiveTab('pending')}
          className={`flex-1 rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
            activeTab === 'pending'
              ? 'bg-background text-foreground shadow-xs'
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          Pending
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('sent')}
          className={`flex-1 rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
            activeTab === 'sent'
              ? 'bg-background text-foreground shadow-xs'
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          Sent
        </button>
      </div>

      <div className="mt-2 flex-1 overflow-y-auto">
        {isLoading ? (
          <Skeleton />
        ) : items.length === 0 ? (
          <EmptyState label={emptyLabel} />
        ) : (
          <div className="space-y-0.5">
            {items.map((request) => (
              <RequestItem key={request.id} request={request} />
            ))}
          </div>
        )}
      </div>

      <AddFriendModal open={isAddFriendOpen} onClose={() => setIsAddFriendOpen(false)} />
    </aside>
  )
}
