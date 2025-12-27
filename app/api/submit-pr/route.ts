import { type NextRequest, NextResponse } from "next/server"
import { exec } from "child_process"
import path from "path"
import { promisify } from "util"

const execAsync = promisify(exec)

export async function POST(request: NextRequest) {
    try {
        const body = await request.json()
        const { prUrl } = body

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
        const command = `python "${scriptPath}" "${prUrl}"`

        console.log(`[API] Executing command: ${command}`)

        try {
            const { stdout, stderr } = await execAsync(command)

            console.log('[Python Script Output]:', stdout)

            // Warnings might appear in stderr, but execution might be successful
            if (stderr) {
                console.warn('[Python Script Stderr]:', stderr)
            }

            return NextResponse.json({
                success: true,
                message: 'PR analysis triggered successfully',
                output: stdout,
                debug_stderr: stderr
            })
        } catch (execError: any) {
            console.error('[API] Exec execution failed:', execError)
            console.error('[API] Stderr:', execError.stderr)
            console.error('[API] Stdout:', execError.stdout)

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
