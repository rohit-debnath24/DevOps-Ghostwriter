import { type NextRequest, NextResponse } from "next/server"
import { getSession } from "@/lib/jwt"

export async function GET(
    request: NextRequest,
    { params }: { params: { id: string } }
) {
    const session = await getSession()

    if (!session) {
        return NextResponse.json({
            error: 'Not authenticated. Please log in first.'
        }, { status: 401 })
    }

    try {
        const repoId = parseInt(params.id)

        if (isNaN(repoId)) {
            return NextResponse.json({
                error: 'Invalid repository ID'
            }, { status: 400 })
        }

        // Get repository details first
        const repoResponse = await fetch(`${request.nextUrl.origin}/api/repositories/${repoId}`, {
            headers: {
                cookie: request.headers.get('cookie') || ''
            }
        })

        if (!repoResponse.ok) {
            return NextResponse.json({
                error: 'Repository not found'
            }, { status: 404 })
        }

        const repo = await repoResponse.json()

        // Fetch contributors from GitHub API
        const githubToken = process.env.GITHUB_TOKEN

        if (!githubToken) {
            return NextResponse.json({
                error: 'GitHub token not configured'
            }, { status: 500 })
        }

        const githubResponse = await fetch(
            `https://api.github.com/repos/${repo.owner}/${repo.name}/contributors?per_page=20`,
            {
                headers: {
                    'Authorization': `Bearer ${githubToken}`,
                    'Accept': 'application/vnd.github.v3+json'
                }
            }
        )

        if (!githubResponse.ok) {
            throw new Error(`GitHub API error: ${githubResponse.status}`)
        }

        const contributors = await githubResponse.json()

        // Transform the data
        const transformedContributors = contributors.map((contributor: any, index: number) => ({
            id: contributor.id,
            name: contributor.login,
            avatar: contributor.avatar_url,
            commits: contributor.contributions,
            prs: Math.floor(contributor.contributions * 0.3), // Estimate based on contributions
            role: index === 0 ? 'Lead Developer' : index < 3 ? 'Senior Dev' : index < 5 ? 'Developer' : 'Junior Dev',
            profileUrl: contributor.html_url
        }))

        return NextResponse.json(transformedContributors)
    } catch (error: any) {
        console.error('Error fetching contributors:', error)
        return NextResponse.json({
            error: error.message || 'Failed to fetch contributors'
        }, { status: 500 })
    }
}
