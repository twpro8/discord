import { useState } from 'react'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import { useRegisterMutation } from '../model/mutations'

export function RegisterForm() {
  const [name, setName] = useState('')
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const registerMutation = useRegisterMutation()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    registerMutation.mutate({ name, username, email, password })
  }

  return (
    <form onSubmit={handleSubmit} className="flex w-full max-w-sm flex-col gap-5">
      <div className="flex flex-col gap-1">
        <h1 className="text-[28px]/-[34px] font-[650] text-[#f3f5f7]">
          Create account
        </h1>
        <p className="text-sm text-[#aab1bf]">
          Join Lumiere
        </p>
      </div>

      <div className="flex flex-col gap-4">
        <div className="flex flex-col gap-2">
          <Label htmlFor="name">Display name</Label>
          <Input
            id="name"
            type="text"
            placeholder="your name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>

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
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            placeholder="your@email.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoComplete="email"
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
            autoComplete="new-password"
          />
        </div>
      </div>

      {registerMutation.isError && (
        <p className="text-sm text-[#f17878]">
          {registerMutation.error instanceof Error
            ? registerMutation.error.message
            : 'Registration failed'}
        </p>
      )}

      <Button type="submit" disabled={registerMutation.isPending} className="w-full">
        {registerMutation.isPending ? 'Creating account...' : 'Create account'}
      </Button>

      <p className="text-center text-sm text-[#737b8b]">
        Already have an account?{' '}
        <a
          href="/login"
          className="font-medium text-[#7c8cff] hover:text-[#93a0ff]"
        >
          Sign in
        </a>
      </p>
    </form>
  )
}
