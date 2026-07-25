import { useMutation } from '@tanstack/react-query'
import { useRouter } from '@tanstack/react-router'
import { registerUser } from '../../api/register'

export function useRegisterMutation() {
  const router = useRouter()

  return useMutation({
    mutationFn: registerUser,
    onSuccess: () => {
      router.navigate({ to: '/login' })
    },
  })
}
