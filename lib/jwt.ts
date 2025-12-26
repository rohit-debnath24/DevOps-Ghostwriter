import jwt from 'jsonwebtoken'
import { v4 as uuidv4 } from 'uuid'
import { cookies } from 'next/headers'

const JWT_SECRET = process.env.JWT_SECRET || 'fallback-secret-key-change-in-production'
const JWT_EXPIRES_IN = process.env.JWT_EXPIRES_IN || '7d'

export interface SessionPayload {
    sessionId: string
    userId: string
    email: string
    name?: string
    provider?: 'local' | 'github' | 'google'
    iat?: number
    exp?: number
}

/**
 * Generate a new session ID using UUID v4
 */
export function generateSessionId(): string {
    return uuidv4()
}

/**
 * Create a JWT token for a user session
 */
export function createSessionToken(payload: Omit<SessionPayload, 'sessionId' | 'iat' | 'exp'>): string {
    const sessionId = generateSessionId()

    const tokenPayload: SessionPayload = {
        ...payload,
        sessionId,
    }

    return jwt.sign(tokenPayload, JWT_SECRET, {
        expiresIn: JWT_EXPIRES_IN,
    } as jwt.SignOptions)
}

/**
 * Verify and decode a JWT token
 */
export function verifySessionToken(token: string): SessionPayload | null {
    try {
        const decoded = jwt.verify(token, JWT_SECRET) as SessionPayload
        return decoded
    } catch (error) {
        console.error('JWT verification failed:', error)
        return null
    }
}

/**
 * Set session cookie with JWT token
 */
export async function setSessionCookie(token: string) {
    const cookieStore = await cookies()

    cookieStore.set('session', token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        maxAge: 60 * 60 * 24 * 7, // 7 days
        path: '/',
    })
}

/**
 * Get session from cookie
 */
export async function getSession(): Promise<SessionPayload | null> {
    const cookieStore = await cookies()
    const sessionCookie = cookieStore.get('session')

    if (!sessionCookie) {
        return null
    }

    return verifySessionToken(sessionCookie.value)
}

/**
 * Clear session cookie
 */
export async function clearSessionCookie() {
    const cookieStore = await cookies()
    cookieStore.delete('session')
}

/**
 * Set GitHub token cookie (for API access)
 */
export async function setGitHubTokenCookie(token: string) {
    const cookieStore = await cookies()

    cookieStore.set('github_token', token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        maxAge: 60 * 60 * 24 * 365, // 1 year (GitHub tokens don't expire)
        path: '/',
    })
}

/**
 * Set Google token cookie (for API access)
 */
export async function setGoogleTokenCookie(token: string) {
    const cookieStore = await cookies()

    cookieStore.set('google_token', token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        maxAge: 60 * 60 * 24 * 365, // 1 year
        path: '/',
    })
}
