// features
import { LoginForm } from "@/features/auth/login/ui/LoginForm";

/** Login page with centered login form. */
export default function LoginPage() {
  return (
    <div className="flex min-h-screen w-full items-center justify-center bg-canvas">
      <LoginForm />
    </div>
  );
}
