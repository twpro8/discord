import type { FormEvent, ReactNode } from 'react'
import { cn } from '@/shared/helpers/utils'

type AuthFormShellProps = {
  title: string
  description: string
  children: ReactNode
  onSubmit: (event: FormEvent<HTMLFormElement>) => void
  className?: string
}

export function AuthFormShell({
  title,
  description,
  children,
  onSubmit,
  className,
}: AuthFormShellProps) {
  return (
    <form onSubmit={onSubmit} className={cn('flex w-full max-w-sm flex-col gap-5', className)}>
      <div className="flex flex-col gap-1">
        <h1 className="text-[28px]/[34px] font-semibold text-foreground">{title}</h1>
        <p className="text-sm text-muted-foreground">{description}</p>
      </div>

      <div className="flex flex-col gap-4">{children}</div>
    </form>
  )
}
