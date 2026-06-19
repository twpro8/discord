import * as z from "zod"

const loginFormSchema = z.object({
    username: z
        .string()
        .min(1, "Username is required"),
    password: z
        .string()
        .min(6, "Password is required")
})

const signupFormSchema = z
    .object({
        email: z.email(),
        username: z.string().min(1, { message: "Username is required" }),
        name: z.string().min(1, { message: "Full Name is required" }),
        password: z
            .string()
            .min(1, { message: "Password is required" })
            .min(6, { message: "Password must be at least 6 characters" }),
        confirmPassword: z
            .string()
            .min(1, { message: "Password confirmation is required" }),
    })
    .refine((data) => data.password === data.confirmPassword, {
        message: "The passwords don't match",
        path: ["confirmPassword"],
    })

type SignupFormData = z.infer<typeof signupFormSchema>
type LoginFormData = z.infer<typeof loginFormSchema>

export { loginFormSchema, signupFormSchema }
export type { LoginFormData, SignupFormData }
