import { useState } from 'react'
import { UserPlus } from 'lucide-react'
import { AddFriendModal } from './AddFriendModal'
import { PendingRequestList } from './PendingRequestList'
import { SentRequestList } from './SentRequestList'
import { FriendList } from './FriendList'
import { useFriendRequests } from '../model/use-friend-requests'
import { useFriends } from '../model/use-friends'
import {
  useAcceptFriendRequest,
  useDeleteFriendRequest,
  useRemoveFriend,
} from '../model/use-friend-mutations'

type Tab = 'pending' | 'sent' | 'friends'

const TABS: { key: Tab; label: string }[] = [
  { key: 'pending', label: 'Pending' },
  { key: 'sent', label: 'Sent' },
  { key: 'friends', label: 'Friends' },
]

export function FriendPanel() {
  const [isAddFriendOpen, setIsAddFriendOpen] = useState(false)
  const [activeTab, setActiveTab] = useState<Tab>('pending')

  const { incoming, sent, isLoading: isLoadingRequests } = useFriendRequests()
  const { data: friends = [], isLoading: isLoadingFriends } = useFriends()

  const acceptMutation = useAcceptFriendRequest()
  const deleteMutation = useDeleteFriendRequest()
  const removeMutation = useRemoveFriend()

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
        {TABS.map((tab) => (
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
          <PendingRequestList
            requests={incoming}
            isLoading={isLoadingRequests}
            disabled={acceptMutation.isPending || deleteMutation.isPending}
            onAccept={(id) => acceptMutation.mutate(id)}
            onDecline={(id) => deleteMutation.mutate(id)}
          />
        )}

        {activeTab === 'sent' && (
          <SentRequestList
            requests={sent}
            isLoading={isLoadingRequests}
            disabled={deleteMutation.isPending}
            onCancel={(id) => deleteMutation.mutate(id)}
          />
        )}

        {activeTab === 'friends' && (
          <FriendList
            friends={friends}
            isLoading={isLoadingFriends}
            disabled={removeMutation.isPending}
            onRemove={(id) => removeMutation.mutate(id)}
          />
        )}
      </div>

      <AddFriendModal open={isAddFriendOpen} onClose={() => setIsAddFriendOpen(false)} />
    </aside>
  )
}
