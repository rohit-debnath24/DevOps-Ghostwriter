import connectDB from './mongodb'
import Repository, { IRepository } from '@/models/Repository'

export interface RepositoryData {
    userId: string
    repoId: number
    name: string
    fullName: string
    description?: string
    language?: string
    topics: string[]
    url: string
    stars: number
    forks: number
    owner: string
    isPrivate: boolean
    defaultBranch: string
    lastAnalyzed?: Date
    healthScore?: number
    findings?: number
    status: 'clean' | 'review_required' | 'audit_active' | 'protected'
}

/**
 * Calculate health score based on repository metrics
 */
export function calculateHealthScore(repo: Partial<RepositoryData>): number {
    const baseHealth = 70
    const starsBonus = Math.min((repo.stars || 0) / 100, 20)
    const languageBonus = repo.language ? 10 : 0
    return Math.min(100, Math.floor(baseHealth + starsBonus + languageBonus))
}

/**
 * Determine repository status based on health score
 */
export function determineStatus(healthScore: number): RepositoryData['status'] {
    if (healthScore >= 95) return 'clean'
    if (healthScore >= 85) return 'review_required'
    if (healthScore >= 70) return 'audit_active'
    return 'audit_active'
}

/**
 * Save or update repositories for a user
 */
export async function saveRepositories(userId: string, repos: any[]): Promise<IRepository[]> {
    await connectDB()

    const savedRepos: IRepository[] = []

    for (const repo of repos) {
        try {
            const healthScore = calculateHealthScore(repo)
            const status = determineStatus(healthScore)
            const findings = Math.floor((100 - healthScore) / 5)
            const fullName = repo.fullName || `${repo.owner}/${repo.name}`

            const repoData = {
                userId,
                repoId: repo.id,
                name: repo.name,
                fullName,
                description: repo.description || '',
                language: repo.language || 'Unknown',
                topics: repo.topics || [],
                url: repo.url,
                stars: repo.stars || 0,
                forks: repo.forks || 0,
                owner: repo.owner,
                isPrivate: repo.private || false,
                defaultBranch: repo.default_branch || 'main',
                healthScore,
                findings,
                status,
                lastAnalyzed: new Date(),
            }

            // Use both userId and fullName to prevent duplicates
            const savedRepo = await Repository.findOneAndUpdate(
                { userId, fullName },
                { $set: repoData },
                { upsert: true, new: true }
            )

            savedRepos.push(savedRepo)
        } catch (error: any) {
            // Handle duplicate key errors gracefully
            if (error.code === 11000) {
                console.warn(`Duplicate repository detected: ${repo.fullName}, skipping...`)
                // Try to fetch the existing repo instead
                const existingRepo = await Repository.findOne({
                    userId,
                    fullName: repo.fullName || `${repo.owner}/${repo.name}`
                })
                if (existingRepo) {
                    savedRepos.push(existingRepo)
                }
            } else {
                // Re-throw other errors
                console.error(`Error saving repository ${repo.fullName}:`, error)
                throw error
            }
        }
    }

    return savedRepos
}

/**
 * Get repositories for a user
 */
export async function getUserRepositories(userId: string): Promise<IRepository[]> {
    await connectDB()
    return await Repository.find({ userId }).sort({ stars: -1, name: 1 }).lean()
}

/**
 * Get a single repository
 */
export async function getRepository(userId: string, repoId: number): Promise<IRepository | null> {
    await connectDB()
    return await Repository.findOne({ userId, repoId }).lean()
}

/**
 * Delete a repository
 */
export async function deleteRepository(userId: string, repoId: number): Promise<boolean> {
    await connectDB()
    const result = await Repository.deleteOne({ userId, repoId })
    return result.deletedCount > 0
}

/**
 * Update repository analysis results
 */
export async function updateRepositoryAnalysis(
    userId: string,
    repoId: number,
    analysis: {
        healthScore?: number
        findings?: number
        status?: RepositoryData['status']
        lastAnalyzed?: Date
    }
): Promise<IRepository | null> {
    await connectDB()

    return await Repository.findOneAndUpdate(
        { userId, repoId },
        {
            $set: {
                ...analysis,
                lastAnalyzed: analysis.lastAnalyzed || new Date()
            }
        },
        { new: true }
    ).lean()
}
