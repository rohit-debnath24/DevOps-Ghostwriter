import { nanoid } from 'nanoid'

export interface User {
    userId: string
    email: string
    firstName?: string
    lastName?: string
    name?: string
    password?: string // hashed, only for local auth
    provider: 'local' | 'github' | 'google'
    githubId?: string
    googleId?: string
    avatar?: string
    createdAt: Date
    updatedAt: Date
}

/**
 * Generate a unique user ID using nanoid
 */
export function generateUserId(): string {
    return nanoid(16) // 16 character unique ID
}

/**
 * Hash password using Web Crypto API (works in Node.js 20+)
 */
export async function hashPassword(password: string): Promise<string> {
    const encoder = new TextEncoder()
    const data = encoder.encode(password)
    const hashBuffer = await crypto.subtle.digest('SHA-256', data)
    const hashArray = Array.from(new Uint8Array(hashBuffer))
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
}

/**
 * Verify password against hash
 */
export async function verifyPassword(password: string, hash: string): Promise<boolean> {
    const passwordHash = await hashPassword(password)
    return passwordHash === hash
}

/**
 * In-memory user store (replace with database in production)
 */
export const userStore = new Map<string, User>()

/**
 * Find user by email
 */
export function findUserByEmail(email: string): User | undefined {
    for (const user of userStore.values()) {
        if (user.email.toLowerCase() === email.toLowerCase()) {
            return user
        }
    }
    return undefined
}

/**
 * Find user by GitHub ID
 */
export function findUserByGitHubId(githubId: string): User | undefined {
    for (const user of userStore.values()) {
        if (user.githubId === githubId) {
            return user
        }
    }
    return undefined
}

/**
 * Find user by Google ID
 */
export function findUserByGoogleId(googleId: string): User | undefined {
    for (const user of userStore.values()) {
        if (user.googleId === googleId) {
            return user
        }
    }
    return undefined
}

/**
 * Create a new user
 */
export function createUser(userData: Partial<User>): User {
    const user: User = {
        userId: generateUserId(),
        email: userData.email!,
        firstName: userData.firstName,
        lastName: userData.lastName,
        name: userData.name,
        password: userData.password,
        provider: userData.provider || 'local',
        githubId: userData.githubId,
        googleId: userData.googleId,
        avatar: userData.avatar,
        createdAt: new Date(),
        updatedAt: new Date(),
    }

    userStore.set(user.userId, user)
    return user
}

/**
 * Update user
 */
export function updateUser(userId: string, updates: Partial<User>): User | undefined {
    const user = userStore.get(userId)
    if (!user) return undefined

    const updatedUser = {
        ...user,
        ...updates,
        updatedAt: new Date(),
    }

    userStore.set(userId, updatedUser)
    return updatedUser
}
