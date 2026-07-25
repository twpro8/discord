import { useState } from 'react'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import { useLoginMutation } from '../model/mutations'

export function LoginForm() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const loginMutation = useLoginMutation()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    loginMutation.mutate({ username, password })
  }

  return (
    <form onSubmit={handleSubmit} className="flex w-full max-w-sm flex-col gap-5">
      <div className="flex flex-col gap-1">
        <h1 className="text-[28px]/-[34px] font-[650] text-[#f3f5f7]">
          Sign in
        </h1>
        <p className="text-sm text-[#aab1bf]">
          Welcome back to Lumiere
        </p>
      </div>

      <div className="flex flex-col gap-4">
        <div className="flex flex-col gap-2">
          <Label htmlFor="username">Username</Label>
          <Input
            id="username"
            type="text"
            placeholder="your username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            autoComplete="username"
          />
        </div>

        <div className="flex flex-col gap-2">
          <Label htmlFor="password">Password</Label>
          <Input
            id="password"
            type="password"
            placeholder="your password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="current-password"
          />
        </div>
      </div>

      {loginMutation.isError && (
        <p className="text-sm text-[#f17878]">
          {loginMutation.error instanceof Error
            ? loginMutation.error.message
            : 'Invalid credentials'}
        </p>
      )}

      <Button type="submit" disabled={loginMutation.isPending} className="w-full">
        {loginMutation.isPending ? 'Signing in...' : 'Sign in'}
      </Button>

      <p className="text-center text-sm text-[#737b8b]">
        Don&apos;t have an account?{' '}
        <a
          href="/register"
          className="font-medium text-[#7c8cff] hover:text-[#93a0ff]"
        >
          Sign up
        </a>
      </p>
    </form>
  )
}
