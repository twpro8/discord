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
import { useLoginMutation } from "../model/mutations";

/** Login form with username and password fields. */
export function LoginForm() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const loginMutation = useLoginMutation();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loginMutation.mutate({ username, password });
  };

  return (
    <AuthFormShell
      title="Sign in"
      description="Welcome back to Lumiere"
      onSubmit={handleSubmit}
    >
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
        <Label htmlFor="password">Password</Label>
        <Input
          id="password"
          type="password"
          placeholder="your password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          autoComplete="current-password"
        />
      </div>

      <Button
        type="submit"
        disabled={loginMutation.isPending}
        className="w-full"
      >
        {loginMutation.isPending ? "Signing in..." : "Sign in"}
      </Button>

      <p className="text-center text-sm text-text-tertiary">
        Don&apos;t have an account?{" "}
        <Link
          to="/register"
          className="font-medium text-primary hover:text-accent-hover"
        >
          Sign up
        </Link>
      </p>
    </AuthFormShell>
  );
}
