import { useMutation } from '@tanstack/react-query'
import { useRouter } from '@tanstack/react-router'
import { toast } from 'sonner'
import { loginUser } from '../../api/login'
import { registerUser } from '../../api/register'
import { getApiError } from '@/shared/api/errors'

type RegisterPayload = {
  name: string
  username: string
  email: string
  password: string
}

export function useRegisterMutation() {
  const router = useRouter()

  return useMutation({
    mutationFn: async ({ name, username, email, password }: RegisterPayload) => {
      await registerUser({ name, username, email, password })
      return loginUser(username, password)
    },
    onSuccess: () => {
      toast.success('Account created successfully')
      router.navigate({ to: '/home' })
    },
    onError: (error: unknown) => {
      toast.error(getApiError(error))
    },
  })
}
