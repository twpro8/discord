import { useMutation } from '@tanstack/react-query'
import { useRouter } from '@tanstack/react-router'
import { loginUser } from '../../api/login'
import { toast } from 'sonner'
import { getApiError } from '@/shared/api/errors'

export function useLoginMutation() {
  const router = useRouter()

  return useMutation({
    mutationFn: ({ username, password }: { username: string; password: string }) =>
      loginUser(username, password),
    onSuccess: () => {
      router.navigate({ to: '/home' })
    },
    onError: (error: unknown) => {
      toast.error(getApiError(error))
    },
  })
}
