import { api } from '@/shared/api/axios'
import type { Server } from '../../../entities/server/model/types'

export async function getMyServers(): Promise<Server[]> {
  const response = await api.get<Server[]>('/servers')
  return response.data
}
