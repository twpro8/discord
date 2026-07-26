import { useState } from 'react'
import { UserPlus, Check, X, Ban, Trash2 } from 'lucide-react'
import { AddFriendModal } from './AddFriendModal'
import { useFriendRequests } from '../model/use-friend-requests'
import { useFriends } from '../model/use-friends'
import {
  useAcceptFriendRequest,
  useDeleteFriendRequest,
  useRemoveFriend,
} from '../model/use-friend-mutations'
import type { FriendRequestWithUser } from '../model/types'

type Tab = 'pending' | 'sent' | 'friends'

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

function PendingItem({
  request,
  isAccepting,
  isDeclining,
  onAccept,
  onDecline,
}: {
  request: FriendRequestWithUser
  isAccepting: boolean
  isDeclining: boolean
  onAccept: (id: string) => void
  onDecline: (id: string) => void
}) {
  return (
    <div className="flex items-center gap-3 rounded-xl px-3 py-2.5 transition-colors hover:bg-muted/50">
      <AvatarInitial username={request.username} />
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium text-foreground">{request.username}</p>
        <p className="text-xs text-muted-foreground">{timeAgo(request.created_at)}</p>
      </div>
      <div className="flex shrink-0 gap-1">
        <button
          type="button"
          disabled={isAccepting || isDeclining}
          onClick={() => onAccept(request.id)}
          className="flex h-7 w-7 items-center justify-center rounded-md bg-green-500/10 text-green-500 transition-colors hover:bg-green-500/20 disabled:opacity-40"
          aria-label="Accept friend request"
        >
          <Check className="h-4 w-4" />
        </button>
        <button
          type="button"
          disabled={isAccepting || isDeclining}
          onClick={() => onDecline(request.id)}
          className="flex h-7 w-7 items-center justify-center rounded-md bg-red-500/10 text-red-500 transition-colors hover:bg-red-500/20 disabled:opacity-40"
          aria-label="Decline friend request"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  )
}

function SentItem({
  request,
  isCancelling,
  onCancel,
}: {
  request: FriendRequestWithUser
  isCancelling: boolean
  onCancel: (id: string) => void
}) {
  return (
    <div className="flex items-center gap-3 rounded-xl px-3 py-2.5 transition-colors hover:bg-muted/50">
      <AvatarInitial username={request.username} />
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium text-foreground">{request.username}</p>
        <p className="text-xs text-muted-foreground">{timeAgo(request.created_at)}</p>
      </div>
      <button
        type="button"
        disabled={isCancelling}
        onClick={() => onCancel(request.id)}
        className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-muted text-muted-foreground transition-colors hover:bg-destructive/10 hover:text-destructive disabled:opacity-40"
        aria-label="Cancel friend request"
      >
        <Ban className="h-4 w-4" />
      </button>
    </div>
  )
}

function FriendItem({
  request,
  isRemoving,
  onRemove,
}: {
  request: FriendRequestWithUser
  isRemoving: boolean
  onRemove: (id: string) => void
}) {
  return (
    <div className="flex items-center gap-3 rounded-xl px-3 py-2.5 transition-colors hover:bg-muted/50">
      <AvatarInitial username={request.username} />
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium text-foreground">{request.username}</p>
        <p className="text-xs text-muted-foreground">Friend since {new Date(request.updated_at).toLocaleDateString()}</p>
      </div>
      <button
        type="button"
        disabled={isRemoving}
        onClick={() => onRemove(request.id)}
        className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-muted text-muted-foreground transition-colors hover:bg-destructive/10 hover:text-destructive disabled:opacity-40"
        aria-label="Remove friend"
      >
        <Trash2 className="h-4 w-4" />
      </button>
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

  const { incoming, sent, isLoading: isLoadingRequests } = useFriendRequests()
  const { data: friends = [], isLoading: isLoadingFriends } = useFriends()

  const acceptMutation = useAcceptFriendRequest()
  const deleteMutation = useDeleteFriendRequest()
  const removeMutation = useRemoveFriend()

  const tabs: { key: Tab; label: string }[] = [
    { key: 'pending', label: 'Pending' },
    { key: 'sent', label: 'Sent' },
    { key: 'friends', label: 'Friends' },
  ]

  const emptyLabels: Record<Tab, string> = {
    pending: 'No pending requests',
    sent: 'No sent requests',
    friends: 'No friends yet. Add some!',
  }

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
        {tabs.map((tab) => (
          <button
            key={tab.key}
            type="button"
            onClick={() => setActiveTab(tab.key)}
            className={`flex-1 rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
              activeTab === tab.key
                ? 'bg-background text-foreground shadow-xs'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="mt-2 flex-1 overflow-y-auto">
        {activeTab === 'pending' && (
          isLoadingRequests ? (
            <Skeleton />
          ) : incoming.length === 0 ? (
            <EmptyState label={emptyLabels.pending} />
          ) : (
            <div className="space-y-0.5">
              {incoming.map((request) => (
                <PendingItem
                  key={request.id}
                  request={request}
                  isAccepting={acceptMutation.isPending}
                  isDeclining={deleteMutation.isPending}
                  onAccept={(id) => acceptMutation.mutate(id)}
                  onDecline={(id) => deleteMutation.mutate(id)}
                />
              ))}
            </div>
          )
        )}

        {activeTab === 'sent' && (
          isLoadingRequests ? (
            <Skeleton />
          ) : sent.length === 0 ? (
            <EmptyState label={emptyLabels.sent} />
          ) : (
            <div className="space-y-0.5">
              {sent.map((request) => (
                <SentItem
                  key={request.id}
                  request={request}
                  isCancelling={deleteMutation.isPending}
                  onCancel={(id) => deleteMutation.mutate(id)}
                />
              ))}
            </div>
          )
        )}

        {activeTab === 'friends' && (
          isLoadingFriends ? (
            <Skeleton />
          ) : friends.length === 0 ? (
            <EmptyState label={emptyLabels.friends} />
          ) : (
            <div className="space-y-0.5">
              {friends.map((friend) => (
                <FriendItem
                  key={friend.id}
                  request={friend}
                  isRemoving={removeMutation.isPending}
                  onRemove={(id) => removeMutation.mutate(id)}
                />
              ))}
            </div>
          )
        )}
      </div>

      <AddFriendModal open={isAddFriendOpen} onClose={() => setIsAddFriendOpen(false)} />
    </aside>
  )
}
