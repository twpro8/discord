import type { ReactNode } from "react";

import { createTestQueryClient } from "@/testing/render-hook";
import { QueryClientProvider } from "@tanstack/react-query";
import { act, renderHook } from "@testing-library/react";
import { toast } from "sonner";
import { vi } from "vitest";

import type { User } from "@/entities/user/model/types";

import { updateAvatar } from "../../api/update-avatar";
import { useUpdateAvatar } from "../use-update-avatar";

vi.mock("../../api/update-avatar", () => ({ updateAvatar: vi.fn() }));
vi.mock("sonner", () => ({
  toast: { error: vi.fn(), success: vi.fn() },
}));

const updateAvatarMock = vi.mocked(updateAvatar);

function makeUser(avatarUrl: string): User {
  return {
    id: "user-1",
    name: "Ada Lovelace",
    username: "ada",
    email: "ada@example.com",
    avatar_url: avatarUrl,
    is_active: true,
    created_at: "2026-08-08T00:00:00Z",
    updated_at: "2026-08-08T00:00:00Z",
  };
}

describe("useUpdateAvatar", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("immediately replaces the cached user with the upload response", async () => {
    const queryClient = createTestQueryClient();
    const oldUser = makeUser("https://cdn.example.com/avatar-old.png");
    const updatedUser = makeUser("https://cdn.example.com/avatar-new.png");
    queryClient.setQueryData(["current-user"], oldUser);
    updateAvatarMock.mockResolvedValue(updatedUser);

    function QueryProvider({ children }: { children: ReactNode }) {
      return (
        <QueryClientProvider client={queryClient}>
          {children}
        </QueryClientProvider>
      );
    }

    const { result } = renderHook(() => useUpdateAvatar(), {
      wrapper: QueryProvider,
    });

    await act(async () => {
      await result.current.mutateAsync(new File(["avatar"], "avatar.png"));
    });

    expect(queryClient.getQueryData(["current-user"])).toEqual(updatedUser);
    expect(toast.success).toHaveBeenCalledWith("Avatar updated");
  });
});
