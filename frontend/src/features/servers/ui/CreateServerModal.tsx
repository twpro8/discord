import { useState } from 'react'
import { toast } from 'sonner'
import { Modal } from '@/shared/ui/modal'
import { createServer } from '../api/create-server'
import { useServers } from '../model/use-servers'

export function CreateServerModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { invalidate } = useServers()

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()

    if (!name.trim()) {
      toast.error('Server name is required')
      return
    }

    setIsSubmitting(true)

    try {
      await createServer({ name: name.trim(), description: description.trim() || null })
      toast.success('Server created successfully')
      setName('')
      setDescription('')
      await invalidate()
      onClose()
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unable to create server'
      toast.error(message)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Modal open={open} onClose={onClose}>
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-foreground">Create a server</h2>
          <p className="mt-1 text-sm text-muted-foreground">Build your own space for friends and channels.</p>
        </div>
      </div>

      <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
        <div>
          <label className="mb-1 block text-sm font-medium text-foreground" htmlFor="server-name">Server name</label>
          <input id="server-name" value={name} onChange={(event) => setName(event.target.value)} className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none ring-0" placeholder="My server" />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-foreground" htmlFor="server-description">Description</label>
          <textarea id="server-description" value={description} onChange={(event) => setDescription(event.target.value)} className="min-h-24 w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none ring-0" placeholder="What is this server about?" />
        </div>

        <div className="flex justify-end gap-2">
          <button type="button" className="rounded-lg border border-border px-3 py-2 text-sm text-foreground" onClick={onClose}>Cancel</button>
          <button type="submit" disabled={isSubmitting} className="rounded-lg bg-primary px-3 py-2 text-sm font-medium text-primary-foreground disabled:opacity-60">
            {isSubmitting ? 'Creating...' : 'Create server'}
          </button>
        </div>
      </form>
    </Modal>
  )
}
