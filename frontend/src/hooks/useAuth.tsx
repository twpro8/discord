import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"
import { handleError } from "@/utils.ts";
import useCustomToast from "@/hooks/useCustomToast.tsx";
import { ROUTES } from "@/routes.ts";
import {
    authLoginUserMutation,
    authRegisterUserMutation,
    usersGetCurrentUserOptions
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
        ...authRegisterUserMutation(),
        onSuccess: () => {
            navigate({ to: ROUTES.LOGIN })
            showSuccessToast("You have successfully registered.")
        },
        onError: handleError.bind(showErrorToast),
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ["users"] })
        },
    })

    const loginMutation = useMutation({
        ...authLoginUserMutation(),
        onSuccess: (data) => {
            localStorage.setItem("access_token", data.access_token)
            navigate({ to: ROUTES.DASHBOARD })
            showSuccessToast("You have successfully logged in.")
        },
        onError: handleError.bind(showErrorToast),
    })

    const logout = () => {
        localStorage.removeItem("access_token")
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
