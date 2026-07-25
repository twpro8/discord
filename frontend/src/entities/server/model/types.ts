export interface Server {
  id: string
  name: string
  description: string | null
  icon_url: string | null
  owner_id: string
  member_count: number
  created_at: string
  updated_at: string
  role?: string
  joined_at?: string
}
