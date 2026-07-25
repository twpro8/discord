import { useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { toast } from 'sonner'
import { getCurrentUser } from '../api/get-me'
import { useUserStore } from '@/shared/model/user-store'
import { clearAuthState } from '@/shared/helpers/auth'

export function useCurrentUser() {
  const { setUser, setLoading, setError, clear } = useUserStore()

  const query = useQuery({
    queryKey: ['current-user'],
    queryFn: getCurrentUser,
    retry: false,
    staleTime: 5 * 60 * 1000,
  })

  useEffect(() => {
    setLoading(query.isLoading)

    if (query.isPending) {
      return
    }

    if (query.data) {
      setUser(query.data)
      setError(null)
      return
    }

    if (query.isError) {
      const message = query.error instanceof Error ? query.error.message : 'Unable to load profile'
      setError(message)
      clearAuthState()
      clear()
      toast.error(message)
    }
  }, [clear, query.data, query.error, query.isError, query.isPending, query.isLoading, setError, setLoading, setUser])

  return query
}
