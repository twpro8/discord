import { useState } from 'react'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import { AuthFormShell } from '../../shared/ui/AuthFormShell'
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
    <AuthFormShell
      title="Sign in"
      description="Welcome back to Lumiere"
      onSubmit={handleSubmit}
    >
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

      <Button type="submit" disabled={loginMutation.isPending} className="w-full">
        {loginMutation.isPending ? 'Signing in...' : 'Sign in'}
      </Button>

      <p className="text-center text-sm text-text-tertiary">
        Don&apos;t have an account?{' '}
        <a
          href="/register"
          className="font-medium text-primary hover:text-accent-hover"
        >
          Sign up
        </a>
      </p>
    </AuthFormShell>
  )
}
