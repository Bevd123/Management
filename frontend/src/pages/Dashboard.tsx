import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'

interface User {
    id: number
    username: string
    role: string
    department: string | null
}

interface Department {
    id: number
    name: string
}

export default function Dashboard() {
    const { user, logout } = useAuth()
    const [users, setUsers] = useState<User[]>([])
    const [departments, setDepartments] = useState<Department[]>([])
    const [isLoadingUsers, setIsLoadingUsers] = useState(false)
    const [error, setError] = useState('')

    // Edit User State
    const [editingUser, setEditingUser] = useState<User | null>(null)
    const [editRole, setEditRole] = useState('')
    const [editDept, setEditDept] = useState('')
    const [editUsername, setEditUsername] = useState('')
    const [editPassword, setEditPassword] = useState('')

    // Create User State
    const [isCreating, setIsCreating] = useState(false)
    const [newUserUsername, setNewUserUsername] = useState('')
    const [newUserPassword, setNewUserPassword] = useState('')
    const [newUserRole, setNewUserRole] = useState('Mitarbeiter')
    const [newUserDept, setNewUserDept] = useState('')

    // Department Management State
    const [newDeptName, setNewDeptName] = useState('')

    // Edit Department State
    const [editingDept, setEditingDept] = useState<Department | null>(null)
    const [editDeptName, setEditDeptName] = useState('')

    useEffect(() => {
        if (user && (user.role === 'Manager' || user.role === 'Geschäftsführer')) {
            fetchUsers()
            fetchDepartments()
        }
    }, [user])

    const fetchUsers = async () => {
        setIsLoadingUsers(true)
        setError('')
        try {
            const token = localStorage.getItem('token')
            const response = await fetch('/users/', {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (response.ok) {
                const data = await response.json()
                setUsers(data)
            } else {
                setError('Fehler beim Laden der Benutzer')
            }
        } catch (err) {
            setError('Netzwerkfehler')
        } finally {
            setIsLoadingUsers(false)
        }
    }

    const fetchDepartments = async () => {
        try {
            const token = localStorage.getItem('token')
            const response = await fetch('/departments/', {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (response.ok) {
                const data = await response.json()
                setDepartments(data)
                if (data.length > 0 && !newUserDept) {
                    setNewUserDept(data[0].name)
                }
            }
        } catch (err) {
            console.error('Failed to fetch departments', err)
        }
    }

    const handleCreateDepartment = async () => {
        try {
            const token = localStorage.getItem('token')
            const response = await fetch('/departments/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ name: newDeptName })
            })
            if (response.ok) {
                setNewDeptName('')
                fetchDepartments()
            } else {
                alert('Fehler beim Erstellen der Abteilung')
            }
        } catch (error) {
            alert('Netzwerkfehler')
        }
    }

    const handleSaveDepartment = async () => {
        if (!editingDept) return
        try {
            const token = localStorage.getItem('token')
            const response = await fetch(`/departments/${editingDept.id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ name: editDeptName })
            })
            if (response.ok) {
                setEditingDept(null)
                fetchDepartments()
                fetchUsers() // Refresh users as their dept might have changed
            } else {
                alert('Fehler beim Speichern (Name existiert evtl. schon)')
            }
        } catch (error) {
            alert('Netzwerkfehler')
        }
    }

    const handleDeleteDepartment = async (id: number) => {
        if (!confirm('Abteilung wirklich löschen?')) return
        try {
            const token = localStorage.getItem('token')
            const response = await fetch(`/departments/${id}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            })
            if (response.ok) {
                fetchDepartments()
            } else {
                alert('Fehler beim Löschen')
            }
        } catch (error) {
            alert('Netzwerkfehler')
        }
    }

    const handleEditClick = (targetUser: User) => {
        setEditingUser(targetUser)
        setEditRole(targetUser.role || 'Mitarbeiter')
        setEditDept(targetUser.department || (departments[0]?.name || ''))
        setEditUsername(targetUser.username)
        setEditPassword('')
    }

    const handleCreateUser = async () => {
        try {
            const token = localStorage.getItem('token')
            const payload = {
                username: newUserUsername,
                password: newUserPassword,
                role: newUserRole,
                department: newUserRole === 'Geschäftsführer' ? 'Management' : newUserDept
            }

            const response = await fetch('/users/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            })

            if (response.ok) {
                setIsCreating(false)
                setNewUserUsername('')
                setNewUserPassword('')
                fetchUsers()
            } else {
                const errData = await response.json()
                alert(`Fehler: ${errData.detail || 'Unbekannter Fehler'}`)
            }
        } catch (error) {
            alert('Netzwerkfehler')
        }
    }

    const handleSaveUser = async () => {
        if (!editingUser) return

        try {
            const token = localStorage.getItem('token')
            const payload: any = {
                role: editRole,
                department: editRole === 'Geschäftsführer' ? 'Management' : editDept,
                username: editUsername
            }

            if (editPassword) {
                payload.password = editPassword
            }

            const response = await fetch(`/users/${editingUser.id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            })

            if (response.ok) {
                setEditingUser(null)
                fetchUsers()
            } else {
                const errData = await response.json()
                alert(`Fehler: ${errData.detail || 'Unbekannter Fehler'}`)
            }
        } catch (error) {
            alert('Netzwerkfehler')
        }
    }

    const getRoleBadgeColor = (role: string) => {
        switch (role) {
            case 'Geschäftsführer':
                return 'bg-purple-500/20 text-purple-300 border-purple-500/30'
            case 'Manager':
                return 'bg-blue-500/20 text-blue-300 border-blue-500/30'
            case 'Mitarbeiter':
                return 'bg-green-500/20 text-green-300 border-green-500/30'
            case 'Pending':
                return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30'
            default:
                return 'bg-zinc-500/20 text-zinc-300 border-zinc-500/30'
        }
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-zinc-950 via-zinc-900 to-zinc-950 text-white">
            <header className="border-b border-white/10 backdrop-blur-xl bg-white/5 p-4">
                <div className="max-w-7xl mx-auto flex justify-between items-center">
                    <h1 className="text-2xl font-bold">Dashboard</h1>
                    <button onClick={logout} className="px-4 py-2 bg-red-500/20 text-red-300 rounded hover:bg-red-500/30">Abmelden</button>
                </div>
            </header>

            <main className="max-w-7xl mx-auto p-4 py-8 space-y-8">
                {error && <div className="p-4 bg-red-500/10 border border-red-500/30 text-red-300 rounded">{error}</div>}

                <div className="p-6 bg-white/5 border border-white/10 rounded-xl">
                    <h2 className="text-xl font-semibold mb-2">Hallo, {user?.username}</h2>
                    <div className="flex gap-4">
                        <span className={`px-3 py-1 rounded-full border ${getRoleBadgeColor(user?.role || '')}`}>
                            {user?.role}
                        </span>
                        <span className="px-3 py-1 rounded-full border border-white/10 bg-white/5">
                            {user?.department || 'Keine Abteilung'}
                        </span>
                    </div>
                </div>

                {/* Department Management (CEO Only) */}
                {user?.role === 'Geschäftsführer' && (
                    <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                        <h2 className="text-xl font-semibold mb-4">Abteilungen verwalten</h2>
                        <div className="flex gap-2 mb-4">
                            <input
                                type="text"
                                placeholder="Neue Abteilung..."
                                value={newDeptName}
                                onChange={e => setNewDeptName(e.target.value)}
                                className="bg-black/20 border border-white/10 rounded p-2 text-white flex-1 max-w-xs"
                            />
                            <button
                                onClick={handleCreateDepartment}
                                className="px-4 py-2 bg-blue-600/20 text-blue-300 border border-blue-500/30 rounded hover:bg-blue-600/30"
                            >
                                + Hinzufügen
                            </button>
                        </div>
                        <div className="flex flex-wrap gap-2">
                            {departments.map(dept => (
                                <div key={dept.id} className="flex items-center gap-2 px-3 py-1 bg-white/5 border border-white/10 rounded-full group">
                                    <span>{dept.name}</span>
                                    <div className="flex gap-1 ml-2 border-l border-white/10 pl-2">
                                        <button
                                            onClick={() => { setEditingDept(dept); setEditDeptName(dept.name); }}
                                            className="text-blue-400 hover:text-blue-300 text-xs uppercase font-bold"
                                        >
                                            Edit
                                        </button>
                                        <button
                                            onClick={() => handleDeleteDepartment(dept.id)}
                                            className="text-red-400 hover:text-red-300 text-xs uppercase font-bold"
                                        >
                                            Del
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Admin Interface */}
                {(user?.role === 'Manager' || user?.role === 'Geschäftsführer') && (
                    <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                        <div className="flex justify-between items-center mb-4">
                            <h2 className="text-xl font-semibold">Mitarbeiter Verwaltung</h2>
                            {user.role === 'Geschäftsführer' && (
                                <button
                                    onClick={() => setIsCreating(true)}
                                    className="px-4 py-2 bg-green-600/20 text-green-300 border border-green-500/30 rounded hover:bg-green-600/30"
                                >
                                    + Neuer Mitarbeiter
                                </button>
                            )}
                        </div>

                        {isLoadingUsers ? <p>Laden...</p> : (
                            <div className="overflow-x-auto">
                                <table className="w-full text-left">
                                    <thead>
                                        <tr className="border-b border-white/10 text-zinc-400">
                                            <th className="p-3">Username</th>
                                            <th className="p-3">Rolle</th>
                                            <th className="p-3">Abteilung</th>
                                            {user.role === 'Geschäftsführer' && <th className="p-3">Aktion</th>}
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {users.map(u => (
                                            <tr key={u.id} className="border-b border-white/5 hover:bg-white/5">
                                                <td className="p-3">{u.username}</td>
                                                <td className="p-3">
                                                    <span className={`px-2 py-0.5 rounded text-xs ${getRoleBadgeColor(u.role)}`}>
                                                        {u.role}
                                                    </span>
                                                </td>
                                                <td className="p-3">{u.department || '-'}</td>
                                                {user.role === 'Geschäftsführer' && (
                                                    <td className="p-3">
                                                        <button
                                                            onClick={() => handleEditClick(u)}
                                                            className="text-blue-400 hover:text-blue-300 text-sm"
                                                        >
                                                            Bearbeiten
                                                        </button>
                                                    </td>
                                                )}
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>
                )}

                {/* Edit Department Modal */}
                {editingDept && (
                    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
                        <div className="bg-zinc-900 border border-white/10 p-6 rounded-xl w-full max-w-sm shadow-2xl">
                            <h3 className="text-lg font-bold mb-4">Abteilung umbenennen</h3>
                            <input
                                type="text"
                                value={editDeptName}
                                onChange={e => setEditDeptName(e.target.value)}
                                className="w-full bg-black/20 border border-white/10 rounded p-2 text-white mb-4"
                            />
                            <p className="text-xs text-zinc-400 mb-4">
                                ⚠ Dies aktualisiert auch alle zugehörigen Mitarbeiter.
                            </p>
                            <div className="flex justify-end gap-2">
                                <button
                                    onClick={() => setEditingDept(null)}
                                    className="px-4 py-2 hover:bg-white/10 rounded"
                                >
                                    Abbrechen
                                </button>
                                <button
                                    onClick={handleSaveDepartment}
                                    className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded text-white"
                                >
                                    Speichern
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Edit User Modal */}
                {editingUser && (
                    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
                        <div className="bg-zinc-900 border border-white/10 p-6 rounded-xl w-full max-w-md shadow-2xl">
                            <h3 className="text-xl font-bold mb-4">Benutzer bearbeiten: {editingUser.username}</h3>

                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm text-zinc-400 mb-1">Benutzername</label>
                                    <input
                                        type="text"
                                        value={editUsername}
                                        onChange={e => setEditUsername(e.target.value)}
                                        className="w-full bg-black/20 border border-white/10 rounded p-2 text-white"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm text-zinc-400 mb-1">Neues Passwort (optional)</label>
                                    <input
                                        type="password"
                                        value={editPassword}
                                        onChange={e => setEditPassword(e.target.value)}
                                        placeholder="Leer lassen zum Beibehalten"
                                        className="w-full bg-black/20 border border-white/10 rounded p-2 text-white"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm text-zinc-400 mb-1">Rolle</label>
                                    <select
                                        value={editRole}
                                        onChange={e => setEditRole(e.target.value)}
                                        className="w-full bg-black/20 border border-white/10 rounded p-2 text-white"
                                    >
                                        <option value="Mitarbeiter">Mitarbeiter</option>
                                        <option value="Manager">Manager</option>
                                        <option value="Geschäftsführer">Geschäftsführer</option>
                                        <option value="Pending">Pending</option>
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-sm text-zinc-400 mb-1">Abteilung</label>
                                    <select
                                        value={editDept}
                                        onChange={e => setEditDept(e.target.value)}
                                        className="w-full bg-black/20 border border-white/10 rounded p-2 text-white"
                                        disabled={editRole === 'Geschäftsführer'}
                                    >
                                        {departments.map(dept => (
                                            <option key={dept.id} value={dept.name}>{dept.name}</option>
                                        ))}
                                        {!departments.some(d => d.name === editDept) && editDept && (
                                            <option value={editDept}>{editDept}</option>
                                        )}
                                    </select>
                                </div>

                                <div className="flex justify-end gap-2 mt-6">
                                    <button
                                        onClick={() => setEditingUser(null)}
                                        className="px-4 py-2 hover:bg-white/10 rounded"
                                    >
                                        Abbrechen
                                    </button>
                                    <button
                                        onClick={handleSaveUser}
                                        className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded text-white"
                                    >
                                        Speichern
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Create User Modal */}
                {isCreating && (
                    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
                        <div className="bg-zinc-900 border border-white/10 p-6 rounded-xl w-full max-w-md shadow-2xl">
                            <h3 className="text-xl font-bold mb-4">Neuen Mitarbeiter anlegen</h3>

                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm text-zinc-400 mb-1">Benutzername</label>
                                    <input
                                        type="text"
                                        value={newUserUsername}
                                        onChange={e => setNewUserUsername(e.target.value)}
                                        className="w-full bg-black/20 border border-white/10 rounded p-2 text-white"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm text-zinc-400 mb-1">Passwort</label>
                                    <input
                                        type="password"
                                        value={newUserPassword}
                                        onChange={e => setNewUserPassword(e.target.value)}
                                        className="w-full bg-black/20 border border-white/10 rounded p-2 text-white"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm text-zinc-400 mb-1">Rolle</label>
                                    <select
                                        value={newUserRole}
                                        onChange={e => setNewUserRole(e.target.value)}
                                        className="w-full bg-black/20 border border-white/10 rounded p-2 text-white"
                                    >
                                        <option value="Mitarbeiter">Mitarbeiter</option>
                                        <option value="Manager">Manager</option>
                                        <option value="Geschäftsführer">Geschäftsführer</option>
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-sm text-zinc-400 mb-1">Abteilung</label>
                                    <select
                                        value={newUserDept}
                                        onChange={e => setNewUserDept(e.target.value)}
                                        className="w-full bg-black/20 border border-white/10 rounded p-2 text-white"
                                        disabled={newUserRole === 'Geschäftsführer'}
                                    >
                                        {departments.map(dept => (
                                            <option key={dept.id} value={dept.name}>{dept.name}</option>
                                        ))}
                                    </select>
                                </div>

                                <div className="flex justify-end gap-2 mt-6">
                                    <button
                                        onClick={() => setIsCreating(false)}
                                        className="px-4 py-2 hover:bg-white/10 rounded"
                                    >
                                        Abbrechen
                                    </button>
                                    <button
                                        onClick={handleCreateUser}
                                        className="px-4 py-2 bg-green-600 hover:bg-green-500 rounded text-white"
                                    >
                                        Anlegen
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </main>
        </div>
    )
}
