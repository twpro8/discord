// features
import { RegisterForm } from "@/features/auth/register/ui/RegisterForm";
import { ServerSettingsButton } from "@/features/profile/ui/ServerSettingsButton";

/** Registration page with centered registration form. */
export default function RegisterPage() {
  return (
    <div className="flex min-h-screen w-full items-center justify-center bg-canvas">
      <ServerSettingsButton />
      <RegisterForm />
    </div>
  );
}
