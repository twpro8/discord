// features
import { LoginForm } from "@/features/auth/login/ui/LoginForm";
import { ServerSettingsButton } from "@/features/profile/ui/ServerSettingsButton";

/** Login page with centered login form. */
export default function LoginPage() {
  return (
    <div className="flex min-h-screen w-full items-center justify-center bg-canvas">
      <ServerSettingsButton />
      <LoginForm />
    </div>
  );
}
