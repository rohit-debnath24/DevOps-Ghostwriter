import { type NextRequest, NextResponse } from "next/server"
import { exec } from "child_process"
import path from "path"
import { promisify } from "util"

const execAsync = promisify(exec)

export async function POST(request: NextRequest) {
    try {
        const body = await request.json()
        const { prUrl, email } = body

        if (!prUrl) {
            return NextResponse.json({
                error: 'PR URL is required'
            }, { status: 400 })
        }

        // Validate URL format basic check
        if (!prUrl.includes('github.com') || !prUrl.includes('/pull/')) {
            return NextResponse.json({
                error: 'Invalid GitHub PR URL provided'
            }, { status: 400 })
        }

        console.log(`[API] Triggering python script for PR: ${prUrl}`)

        // Path to the python script
        const scriptPath = path.resolve(process.cwd(), 'fetch_real_pr.py')

        // Construct command with optional email
        let command = `python "${scriptPath}" "${prUrl}"`
        if (email) {
            command += ` --email "${email}"`
        }

        console.log(`[API] Executing command: ${command}`)

        try {
            const { stdout, stderr } = await execAsync(command)

            console.log('[Python Script Output]:', stdout)

            // Warnings might appear in stderr, but execution might be successful
            if (stderr) {
                console.warn('[Python Script Stderr]:', stderr)
            }

            return NextResponse.json({
                error: `Failed to fetch PR from GitHub (${ghRes.status})`
            }, { status: ghRes.status })
        }

        const prData = await ghRes.json()

        // 3. Construct Payload for Backend
        const payload = {
            action: "opened",
            pull_request: {
                number: prNumber,
                title: prData.title || `PR #${prNumber}`,
                body: prData.body || "No description provided",
                html_url: prData.html_url || prUrl,
                diff_url: prData.diff_url || ""
            },
            repository: {
                name: repo,
                owner: { login: owner },
                full_name: `${owner}/${repo}`
            },
            email: email || null, // Use provided email or let backend rely on payload defaults
            github_token: request.cookies.get('github_token')?.value || null
        }

        // 4. Forward to Node.js Backend
        const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:3001'
        const targetUrl = `${backendUrl}/api/webhook/github`

        console.log(`[API] Forwarding to Backend: ${targetUrl}`)

        const backendRes = await fetch(targetUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-GitHub-Event': 'pull_request'
            },
            body: JSON.stringify(payload)
        })

        if (!backendRes.ok) {
            const txt = await backendRes.text()
            return NextResponse.json({
                error: 'Failed to execute analysis script',
                details: execError.message,
                stderr: execError.stderr,
                stdout: execError.stdout,
                command: command,
                path_env: process.env.PATH // Debug info
            }, { status: 500 })
        }

    } catch (error: any) {
        console.error('Error submitting PR:', error)
        return NextResponse.json({
            error: error.message || 'Failed to submit PR for analysis'
        }, { status: 500 })
    }
}
