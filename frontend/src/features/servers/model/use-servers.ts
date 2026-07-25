import { useEffect } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { getMyServers } from '../api/get-servers'
import { useUserStore } from '@/shared/model/user-store'
import { toast } from 'sonner'

export function useServers() {
  const queryClient = useQueryClient()
  const { user } = useUserStore()

  const query = useQuery({
    queryKey: ['servers', user?.id],
    queryFn: getMyServers,
    enabled: Boolean(user?.id),
    retry: false,
  })

  useEffect(() => {
    if (query.isError) {
      const message = query.error instanceof Error ? query.error.message : 'Unable to load servers'
      toast.error(message)
    }
  }, [query.error, query.isError])

  return {
    ...query,
    invalidate: () => queryClient.invalidateQueries({ queryKey: ['servers'] }),
  }
}
