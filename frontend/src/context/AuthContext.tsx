import { createContext, useContext, useState, useEffect, ReactNode } from 'react'

interface User {
    id: number
    username: string
    role: string
    department: string
    inventory: any
}

interface AuthContextType {
    user: User | null
    token: string | null
    login: (username: string, password: string) => Promise<void>
    logout: () => void
    isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null)
    const [token, setToken] = useState<string | null>(null)
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        // Check for stored token on mount
        const storedToken = localStorage.getItem('token')
        if (storedToken) {
            setToken(storedToken)
            fetchCurrentUser(storedToken)
        } else {
            setIsLoading(false)
        }
    }, [])

    const fetchCurrentUser = async (authToken: string) => {
        try {
            const response = await fetch('/users/me', {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            })
            if (response.ok) {
                const userData = await response.json()
                setUser(userData)
            } else {
                localStorage.removeItem('token')
                setToken(null)
            }
        } catch (error) {
            console.error('Failed to fetch user:', error)
            localStorage.removeItem('token')
            setToken(null)
        } finally {
            setIsLoading(false)
        }
    }

    const login = async (username: string, password: string) => {
        const formData = new FormData()
        formData.append('username', username)
        formData.append('password', password)

        const response = await fetch('/auth/token', {
            method: 'POST',
            body: formData
        })

        if (!response.ok) {
            throw new Error('Login failed')
        }

        const data = await response.json()
        const newToken = data.access_token

        setToken(newToken)
        localStorage.setItem('token', newToken)

        await fetchCurrentUser(newToken)
    }

    const logout = () => {
        setUser(null)
        setToken(null)
        localStorage.removeItem('token')
    }

    return (
        <AuthContext.Provider value={{ user, token, login, logout, isLoading }}>
            {children}
        </AuthContext.Provider>
    )
}

export function useAuth() {
    const context = useContext(AuthContext)
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider')
    }
    return context
}
