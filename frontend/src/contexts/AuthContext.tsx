import { createContext, useState } from "react"



interface AuthContextType {
    token: string | null
    user: string | null
    login: (user: string, password: string) => Promise<boolean>
    logout: () => void
}
export const API_BASE_URL = 'http://localhost:8000'

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<string | null>(localStorage.getItem('user'))
    const [token, setToken] = useState<string | null>(localStorage.getItem('admin_token'))

    const login = async (user: string, password: string): Promise<boolean> => {
        const response = await fetch(`${API_BASE_URL}/health`, {
            headers: { Authorization: `Bearer ${password}` }
        })
        return false
    }


    return (
        <AuthContext.Provider value={{ token, user, login, logout }}>
            {children}
        </AuthContext.Provider>
    )
}