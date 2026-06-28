import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
    try {
        const body = await request.json()
        const { prUrl, email } = body

        if (!prUrl) {
            return NextResponse.json({
                error: 'PR URL is required'
            }, { status: 400 })
        }

        // Parse URL 
        const match = prUrl.match(/github\.com\/([^/]+)\/([^/]+)\/pull\/(\d+)/);
        if (!match) {
            return NextResponse.json({
                error: 'Invalid GitHub PR URL provided. Expected format: https://github.com/owner/repo/pull/123'
            }, { status: 400 })
        }
        
        const owner = match[1];
        const repo = match[2];
        const prNumber = match[3];

        console.log(`[API] Submitting PR for analysis: ${owner}/${repo} #${prNumber}`)

        const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:3001'
        const targetUrl = `${backendUrl}/api/analyze-pr`

        console.log(`[API] Forwarding to Backend: ${targetUrl}`)

        const backendRes = await fetch(targetUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ owner, repo, pull_number: prNumber, email })
        })

        if (!backendRes.ok) {
            const txt = await backendRes.text()
            return NextResponse.json({
                error: 'Failed to execute analysis script on backend',
                details: txt,
            }, { status: backendRes.status })
        }

        const data = await backendRes.json();
        return NextResponse.json(data);

    } catch (error: any) {
        console.error('Error submitting PR:', error)
        return NextResponse.json({
            error: error.message || 'Failed to submit PR for analysis'
        }, { status: 500 })
    }
}
