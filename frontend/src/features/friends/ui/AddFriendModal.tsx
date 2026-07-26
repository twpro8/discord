import { useState } from 'react'
import { toast } from 'sonner'
import { UserPlus } from 'lucide-react'
import { Modal } from '@/shared/ui/modal'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
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
          <Input
            id="friend-username"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            placeholder="Enter a username"
          />
        </div>

        <div className="flex justify-end gap-2">
          <Button type="button" variant="outline" onClick={onClose}>Cancel</Button>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Sending...' : 'Send request'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
