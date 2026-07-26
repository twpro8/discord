import { createFileRoute, redirect } from '@tanstack/react-router'
import { checkAuth } from '@/shared/helpers/auth'

export const Route = createFileRoute('/')({
  beforeLoad: async () => {
    const authenticated = await checkAuth()

    if (authenticated) {
      throw redirect({ to: '/home' })
    }

    throw redirect({ to: '/login' })
  },
})
