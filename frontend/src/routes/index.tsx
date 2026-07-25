import { createFileRoute, redirect } from '@tanstack/react-router'
import { hasAuthToken } from '@/shared/helpers/auth'

export const Route = createFileRoute('/')({
  beforeLoad: async () => {
    const isAuthenticated = await hasAuthToken()

    if (isAuthenticated) {
      throw redirect({ to: '/home' })
    }

    throw redirect({ to: '/login' })
  },
})
