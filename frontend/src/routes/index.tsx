import { createFileRoute } from '@tanstack/react-router'
import { HelloWorld } from '../helloworld'

export const Route = createFileRoute('/')({
  component: HelloWorld,
})
