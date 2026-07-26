import { useState } from 'react'
import { toast } from 'sonner'
import { UserPlus } from 'lucide-react'
import { Modal } from '@/shared/ui/modal'
import { sendFriendRequest } from '../api/send-friend-request'
import { getApiError } from '@/shared/api/errors'

export function AddFriendModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [username, setUsername] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()

    if (!username.trim()) {
      toast.error('Username is required')
      return
    }

    setIsSubmitting(true)

    try {
      await sendFriendRequest({ username: username.trim() })
      toast.success('Friend request sent')
      setUsername('')
      onClose()
    } catch (error: unknown) {
      toast.error(getApiError(error))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Modal open={open} onClose={onClose}>
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
          <UserPlus className="h-5 w-5 text-primary" />
        </div>
        <div>
          <h2 className="text-xl font-semibold text-foreground">Add friend</h2>
          <p className="mt-0.5 text-sm text-muted-foreground">Send a friend request by username.</p>
        </div>
      </div>

      <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
        <div>
          <label className="mb-1 block text-sm font-medium text-foreground" htmlFor="friend-username">Username</label>
          <input
            id="friend-username"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none ring-0"
            placeholder="Enter a username"
          />
        </div>

        <div className="flex justify-end gap-2">
          <button type="button" className="rounded-lg border border-border px-3 py-2 text-sm text-foreground" onClick={onClose}>Cancel</button>
          <button type="submit" disabled={isSubmitting} className="rounded-lg bg-primary px-3 py-2 text-sm font-medium text-primary-foreground disabled:opacity-60">
            {isSubmitting ? 'Sending...' : 'Send request'}
          </button>
        </div>
      </form>
    </Modal>
  )
}
