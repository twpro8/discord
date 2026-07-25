import { createFileRoute, redirect } from '@tanstack/react-router'
import { getAccessToken } from '@/shared/lib/tokens'

export const Route = createFileRoute('/')({
  beforeLoad: () => {
    const accessToken = getAccessToken()

    if (accessToken) {
      throw redirect({ to: '/home' })
    }

    throw redirect({ to: '/register' })
  },
})
