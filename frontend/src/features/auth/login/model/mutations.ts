import { useMutation } from '@tanstack/react-query'
import { useRouter } from '@tanstack/react-router'
import { loginUser } from '../../api/login'
import { setTokens } from '@/shared/lib/tokens'

export function useLoginMutation() {
  const router = useRouter()

  return useMutation({
    mutationFn: ({ username, password }: { username: string; password: string }) =>
      loginUser(username, password),
    onSuccess: (tokens) => {
      setTokens(tokens.access_token, tokens.refresh_token)
      router.navigate({ to: '/' })
    },
  })
}
