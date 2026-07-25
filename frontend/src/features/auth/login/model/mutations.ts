import { useMutation } from '@tanstack/react-query'
import { useRouter } from '@tanstack/react-router'
import { loginUser } from '../../api/login'

export function useLoginMutation() {
  const router = useRouter()

  return useMutation({
    mutationFn: ({ username, password }: { username: string; password: string }) =>
      loginUser(username, password),
    onSuccess: () => {
      router.navigate({ to: '/' })
    },
  })
}
