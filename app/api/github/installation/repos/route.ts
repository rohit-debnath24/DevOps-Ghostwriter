import { type NextRequest, NextResponse } from "next/server"
import { getSession } from "@/lib/jwt"
import { saveRepositories } from "@/lib/repository"
import { updateUser } from "@/lib/db"
import jwt from 'jsonwebtoken'

function generateGitHubAppJWT() {
    const appId = process.env.GITHUB_APP_ID
    const privateKey = process.env.GITHUB_APP_PRIVATE_KEY

    if (!appId || !privateKey) {
        throw new Error('GitHub App credentials not configured')
    }

    // GitHub requires the private key newlines to be actual newlines
    const formattedPrivateKey = privateKey.replace(/\\n/g, '\n')

    const now = Math.floor(Date.now() / 1000)
    const payload = {
        iat: now - 60, // Issued at time (60 seconds in the past to allow for clock drift)
        exp: now + (10 * 60), // JWT expires in 10 minutes
        iss: appId // GitHub App's identifier
    }

    return jwt.sign(payload, formattedPrivateKey, { algorithm: 'RS256' })
}

async function getInstallationAccessToken(installationId: string) {
    const jwtToken = generateGitHubAppJWT()

    const response = await fetch(
        `https://api.github.com/app/installations/${installationId}/access_tokens`,
        {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${jwtToken}`,
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'DevOps-Ghostwriter'
            }
        }
    )

    if (!response.ok) {
        const errorText = await response.text()
        console.error('Failed to get installation token:', response.status, errorText)
        throw new Error(`Failed to get installation access token: ${response.status}`)
    }

    const data = await response.json()
    return data.token
}

export async function GET(request: NextRequest) {
    const session = await getSession()

    if (!session) {
        return NextResponse.json({
            error: 'Not authenticated. Please log in first.'
        }, { status: 401 })
    }

    // Get installation ID from cookie or query parameter
    const installationId = request.nextUrl.searchParams.get('installation_id') ||
        request.cookies.get('github_installation_id')?.value

    if (!installationId) {
        return NextResponse.json({
            error: 'GitHub App not installed. Please connect your GitHub account first.'
        }, { status: 400 })
    }

    try {
        // Get installation access token
        const accessToken = await getInstallationAccessToken(installationId)

        // Fetch repositories accessible by this installation
        const reposResponse = await fetch(
            'https://api.github.com/installation/repositories',
            {
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'Accept': 'application/vnd.github.v3+json',
                    'User-Agent': 'DevOps-Ghostwriter'
                }
            }
        )

        if (!reposResponse.ok) {
            const errorText = await reposResponse.text()
            console.error('Failed to fetch repositories:', reposResponse.status, errorText)
            throw new Error(`Failed to fetch repositories: ${reposResponse.status}`)
        }

        const data = await reposResponse.json()

        // Transform the data to match our interface
        const transformedRepos = data.repositories.map((repo: any) => ({
            id: repo.id,
            name: repo.name,
            description: repo.description || 'No description available',
            language: repo.language || 'Unknown',
            topics: repo.topics || [],
            url: repo.html_url,
            stars: repo.stargazers_count,
            forks: repo.forks_count,
            owner: repo.owner.login,
            fullName: repo.full_name,
            private: repo.private,
            default_branch: repo.default_branch
        }))

        // Save repositories to database
        await saveRepositories(session.userId, transformedRepos)

        // Update user's installation ID
        await updateUser(session.userId, {
            githubInstallationId: installationId
        })

        console.log(`Saved ${transformedRepos.length} repositories for user ${session.userId}`)

        return NextResponse.json(transformedRepos)

    } catch (error: any) {
        console.error('Error fetching installation repos:', error)
        return NextResponse.json({
            error: error.message || 'Failed to fetch repositories from GitHub App'
        }, { status: 500 })
    }
}
