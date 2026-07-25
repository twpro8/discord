import { create } from 'zustand'
import type { User } from '@/entities/user'

type UserStoreState = {
  user: User | null
  isLoading: boolean
  error: string | null
  setUser: (user: User | null) => void
  setLoading: (value: boolean) => void
  setError: (error: string | null) => void
  clear: () => void
}

const initialState = {
  user: null,
  isLoading: false,
  error: null,
}

export const useUserStore = create<UserStoreState>((set) => ({
  ...initialState,
  setUser: (user) => set({ user }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  clear: () => set(initialState),
}))
