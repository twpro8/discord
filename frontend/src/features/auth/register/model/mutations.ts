import { useMutation } from '@tanstack/react-query'
import { useRouter } from '@tanstack/react-router'
import { loginUser } from '../../api/login'
import { registerUser } from '../../api/register'
import { setTokens } from '@/shared/lib/tokens'

export function useRegisterMutation() {
  const router = useRouter()

  return useMutation({
    mutationFn: async ({ name, username, email, password }: { name: string; username: string; email: string; password: string }) => {
      await registerUser({ name, username, email, password })
      return loginUser(username, password)
    },
    onSuccess: (tokens) => {
      setTokens(tokens.access_token, tokens.refresh_token)
      router.navigate({ to: '/home' })
    },
  })
}
