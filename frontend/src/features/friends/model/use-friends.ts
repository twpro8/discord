import { useQuery } from '@tanstack/react-query'
import { getFriends } from '../api/get-friends'

export function useFriends() {
  return useQuery({
    queryKey: ['friends'],
    queryFn: getFriends,
    retry: false,
  })
}
