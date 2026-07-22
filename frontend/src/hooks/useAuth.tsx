import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"
import { getErrorMessage } from "@/utils";
import useCustomToast from "@/hooks/useCustomToast.tsx";
import { ROUTES } from "@/routes.ts";
import {
    authLoginMutation,
    authRegisterMutation,
    usersGetCurrentUserOptions,
} from "@/client/@tanstack/react-query.gen.ts";

const isLoggedIn = () => {
    return localStorage.getItem("access_token") !== null
}

const useAuth = () => {
    const navigate = useNavigate()
    const queryClient = useQueryClient()
    const { showErrorToast, showSuccessToast } = useCustomToast()

    const { data: user } = useQuery({
        ...usersGetCurrentUserOptions(),
        enabled: isLoggedIn(),
    })

    const signUpMutation = useMutation({
        ...authRegisterMutation(),
        onSuccess: () => {
            navigate({ to: ROUTES.LOGIN })
            showSuccessToast("You have successfully registered.")
        },
        onError: (error) => showErrorToast(getErrorMessage(error)),
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ["users"] })
        },
    })

    const loginMutation = useMutation({
        ...authLoginMutation(),
        onSuccess: (data) => {
            localStorage.setItem("access_token", data.access_token)
            localStorage.setItem("refresh_token", data.refresh_token);
            navigate({ to: ROUTES.DASHBOARD })
            showSuccessToast("You have successfully logged in.")
        },
        onError: (error) => showErrorToast(getErrorMessage(error)),
    })

    const logout = () => {
        localStorage.removeItem("access_token")
        localStorage.removeItem("refresh_token");
        navigate({ to: ROUTES.LOGIN })
    }

    return {
        signUpMutation,
        loginMutation,
        logout,
        user,
    }
}

export { isLoggedIn }
export default useAuth
