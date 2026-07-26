// features
import { RegisterForm } from "@/features/auth/register/ui/RegisterForm";

/** Registration page with centered registration form. */
export default function RegisterPage() {
  return (
    <div className="flex min-h-screen w-full items-center justify-center bg-canvas">
      <RegisterForm />
    </div>
  );
}
