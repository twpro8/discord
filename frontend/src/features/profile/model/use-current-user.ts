import { useQuery } from '@tanstack/react-query'
import { getCurrentUser } from '../api/get-me'

export function useCurrentUser() {
  return useQuery({
    queryKey: ['current-user'],
    queryFn: getCurrentUser,
    retry: false,
    staleTime: 5 * 60 * 1000,
  })
}
