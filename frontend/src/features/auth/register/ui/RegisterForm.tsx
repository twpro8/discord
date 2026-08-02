// react
import { useState } from "react";

// third party
import { Link } from "@tanstack/react-router";

// shared
import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";
import { Label } from "@/shared/ui/label";

// relative
import { AuthFormShell } from "../../shared/ui/AuthFormShell";
import { useRegisterMutation } from "../model/mutations";

/** Registration form with name, username, email, and password fields. */
export function RegisterForm() {
  const [name, setName] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const registerMutation = useRegisterMutation();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    registerMutation.mutate({ name, username, email, password });
  };

  return (
    <AuthFormShell
      title="Create account"
      description="Join Lumiere"
      onSubmit={handleSubmit}
    >
      <div className="flex flex-col gap-2">
        <Label htmlFor="name">Display name</Label>
        <Input
          id="name"
          type="text"
          placeholder="your name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
      </div>

      <div className="flex flex-col gap-2">
        <Label htmlFor="username">Username</Label>
        <Input
          id="username"
          type="text"
          placeholder="your username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
          autoComplete="username"
        />
      </div>

      <div className="flex flex-col gap-2">
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          type="email"
          placeholder="your@email.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          autoComplete="email"
        />
      </div>

      <div className="flex flex-col gap-2">
        <Label htmlFor="password">Password</Label>
        <Input
          id="password"
          type="password"
          placeholder="your password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          autoComplete="new-password"
        />
      </div>

      {registerMutation.isError && (
        <p className="text-sm text-destructive">
          {registerMutation.error instanceof Error
            ? registerMutation.error.message
            : "Registration failed"}
        </p>
      )}

      <Button
        type="submit"
        disabled={registerMutation.isPending}
        className="w-full"
      >
        {registerMutation.isPending ? "Creating account..." : "Create account"}
      </Button>

      <p className="text-center text-sm text-text-tertiary">
        Already have an account?{" "}
        <Link
          to="/login"
          className="font-medium text-primary hover:text-accent-hover"
        >
          Sign in
        </Link>
      </p>
    </AuthFormShell>
  );
}
