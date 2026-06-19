import dayjs from "dayjs"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Field, FieldLabel, FieldSeparator } from "@/components/ui/field"
import useAuth from "@/hooks/useAuth.tsx";

export function RootPage(){
    const { user, logout } = useAuth()
    return (
        <div className="flex min-h-svh w-full flex-col items-center justify-center gap-3 p-6 md:p-10">
            <div>Welcome to Lumiere!👋</div>
            <Card className="w-full max-w-xs">
                <CardHeader>
                    <CardTitle>User Info</CardTitle>
                </CardHeader>
                <FieldSeparator className="*:h-px" />
                <CardContent className="flex flex-col gap-3">
                    <Field className="flex flex-row justify-between">
                        <FieldLabel>Full Name:</FieldLabel>
                        <span className="flex justify-end">{user?.name}</span>
                    </Field>
                    <Field className="flex flex-row justify-between">
                        <FieldLabel>Username:</FieldLabel>
                        <span className="flex justify-end">{user?.username}</span>
                    </Field>
                    <Field className="flex flex-row justify-between">
                        <FieldLabel>Email:</FieldLabel>
                        <span className="flex justify-end">{user?.email}</span>
                    </Field>
                    <Field className="flex flex-row justify-between">
                        <FieldLabel>Registered:</FieldLabel>
                        <span className="flex justify-end">
              {user?.created_at
                  ? dayjs(user.created_at).format("D MMMM YYYY")
                  : "—"}
            </span>
                    </Field>
                    <FieldSeparator className="*:h-px" />
                    <Field>
                        <Button
                            variant="destructive"
                            size="sm"
                            className="w-full"
                            onClick={logout}
                        >
                            Logout
                        </Button>
                    </Field>
                </CardContent>
            </Card>
        </div>
    )
}
