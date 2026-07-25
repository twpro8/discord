import { api } from '@/shared/api/axios'
import type { Server } from '../../../entities/server/model/types'

export interface CreateServerInput {
  name: string
  description: string | null
}

export async function createServer(input: CreateServerInput): Promise<Server> {
  const response = await api.post<Server>('/servers', input)
  return response.data
}
