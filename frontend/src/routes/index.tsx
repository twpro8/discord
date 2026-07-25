import { createFileRoute, redirect } from '@tanstack/react-router'
import { hasAuthToken } from '@/shared/lib/auth'

export const Route = createFileRoute('/')({
  beforeLoad: () => {
    if (hasAuthToken()) {
      throw redirect({ to: '/home' })
    }

    throw redirect({ to: '/register' })
  },
})
