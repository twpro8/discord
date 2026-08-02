// third party
import { useMutation } from "@tanstack/react-query";
import { useRouter } from "@tanstack/react-router";
import { toast } from "sonner";

// shared
import { getApiError } from "@/shared/api/errors";

// relative
import { loginUser } from "../../api/login";
import { registerUser } from "../../api/register";

type RegisterPayload = {
  name: string;
  username: string;
  email: string;
  password: string;
};

/** Mutation that registers, logs in, and navigates to /home on success. */
export function useRegisterMutation() {
  const router = useRouter();

  return useMutation({
    mutationFn: async ({
      name,
      username,
      email,
      password,
    }: RegisterPayload) => {
      await registerUser({ name, username, email, password });
      await loginUser(username, password).catch(() => {});
    },
    onSuccess: () => {
      toast.success("Account created successfully");
      router.navigate({ to: "/home" });
    },
    onError: (error: unknown) => {
      toast.error(getApiError(error));
    },
  });
}
