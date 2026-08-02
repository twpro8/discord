// third party
import { useMutation } from "@tanstack/react-query";
import { useRouter } from "@tanstack/react-router";
import { toast } from "sonner";

// shared
import { getApiError } from "@/shared/api/errors";

// relative
import { loginUser } from "../../api/login";

/** Mutation that logs in and navigates to /home on success. */
export function useLoginMutation() {
  const router = useRouter();

  return useMutation({
    mutationFn: ({
      username,
      password,
    }: {
      username: string;
      password: string;
    }) => loginUser(username, password),
    onSuccess: () => {
      router.navigate({ to: "/home" });
    },
    onError: (error: unknown) => {
      toast.error(getApiError(error));
    },
  });
}
