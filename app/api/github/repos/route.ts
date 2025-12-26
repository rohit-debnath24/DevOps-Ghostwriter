import { type NextRequest, NextResponse } from "next/server"

export async function GET(request: NextRequest) {
    const token = request.cookies.get('github_token')?.value

    console.log('GitHub Token from cookies:', token ? 'Present' : 'Missing')

    if (!token) {
        return NextResponse.json({
            error: 'Not authenticated. Please connect your GitHub account first.'
        }, { status: 401 })
    }

    try {
        // Create AbortController for timeout
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), 8000) // 8 second timeout

        const response = await fetch('https://api.github.com/user/repos?type=public&sort=updated&per_page=20', {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Accept': 'application/vnd.github.v3+json',
                'X-GitHub-Api-Version': '2022-11-28',
                'User-Agent': 'Your-App-Name' // GitHub requires User-Agent
            },
            signal: controller.signal
        })

        clearTimeout(timeoutId)

        if (response.status === 401) {
            return NextResponse.json({
                error: 'GitHub token expired or invalid. Please reconnect your account.'
            }, { status: 401 })
        }

        if (!response.ok) {
            const errorData = await response.text()
            console.error('GitHub API error:', response.status, errorData)
            throw new Error(`GitHub API responded with status ${response.status}`)
        }

        const repos = await response.json()

        // Transform the data to match our interface
        const transformedRepos = repos.map((repo: any) => ({
            id: repo.id,
            name: repo.name,
            description: repo.description || 'No description available',
            language: repo.language || 'Unknown',
            topics: repo.topics || [],
            url: repo.html_url,
            stars: repo.stargazers_count,
            forks: repo.forks_count,
        }))

        return NextResponse.json(transformedRepos)
    } catch (error: any) {
        console.error('Error fetching GitHub repos:', error)

        if (error.name === 'AbortError') {
            return NextResponse.json({
                error: 'Connection to GitHub timed out. Please try again.'
            }, { status: 504 })
        }

        return NextResponse.json({
            error: 'Failed to fetch repositories from GitHub. Please check your internet connection.'
        }, { status: 500 })
    }
}
