import { nanoid } from 'nanoid'
import connectDB from './mongodb'
import User, { IUser } from '@/models/User'

export interface UserData {
    userId: string
    email: string
    firstName?: string
    lastName?: string
    name?: string
    password?: string // hashed, only for local auth
    provider: 'email' | 'github' | 'google'
    githubId?: string
    googleId?: string
    avatar?: string
    githubToken?: string
    googleToken?: string
    githubInstallationId?: string
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
 * Find user by email
 */
export async function findUserByEmail(email: string): Promise<UserData | null> {
    await connectDB()
    const user = await User.findOne({ email: email.toLowerCase() }).lean()
    return user as UserData | null
}

/**
 * Find user by GitHub ID
 */
export async function findUserByGitHubId(githubId: string): Promise<UserData | null> {
    await connectDB()
    const user = await User.findOne({ githubId }).lean()
    return user as UserData | null
}

/**
 * Find user by Google ID
 */
export async function findUserByGoogleId(googleId: string): Promise<UserData | null> {
    await connectDB()
    const user = await User.findOne({ googleId }).lean()
    return user as UserData | null
}

/**
 * Find user by user ID
 */
export async function findUserById(userId: string): Promise<UserData | null> {
    await connectDB()
    const user = await User.findOne({ userId }).lean()
    return user as UserData | null
}

/**
 * Create a new user
 */
export async function createUser(userData: Partial<UserData>): Promise<UserData> {
    await connectDB()

    const user = new User({
        userId: generateUserId(),
        email: userData.email!.toLowerCase(),
        name: userData.name || `${userData.firstName || ''} ${userData.lastName || ''}`.trim(),
        password: userData.password,
        provider: userData.provider || 'email',
        githubId: userData.githubId,
        googleId: userData.googleId,
        avatar: userData.avatar,
        githubToken: userData.githubToken,
        googleToken: userData.googleToken,
        githubInstallationId: userData.githubInstallationId,
    })

    await user.save()
    return user.toObject() as UserData
}

/**
 * Update an existing user
 */
export async function updateUser(userId: string, updates: Partial<UserData>): Promise<UserData | null> {
    await connectDB()

    const user = await User.findOneAndUpdate(
        { userId },
        {
            $set: {
                ...updates,
                updatedAt: new Date()
            }
        },
        { new: true }
    ).lean()

    return user as UserData | null
}
