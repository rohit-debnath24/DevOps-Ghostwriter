import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { firstName, lastName, email, password } = body

    // Validate required fields
    if (!firstName || !lastName || !email || !password) {
      return NextResponse.json(
        {
          success: false,
          message: "All fields are required for operator registration.",
        },
        { status: 400 },
      )
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email)) {
      return NextResponse.json(
        {
          success: false,
          message: "Invalid email format provided.",
        },
        { status: 400 },
      )
    }

    // Validate password strength
    if (password.length < 8) {
      return NextResponse.json(
        {
          success: false,
          message: "Password must be at least 8 characters long.",
        },
        { status: 400 },
      )
    }

    // Mock registration logic - log to console for now
    console.log("[v0] New operator registration attempt:", {
      firstName,
      lastName,
      email,
      timestamp: new Date().toISOString(),
    })

    // TODO: Replace with actual database integration
    // - Hash password with bcrypt
    // - Store user in database
    // - Send verification email
    // - Create session token

    // Simulate successful registration
    return NextResponse.json(
      {
        success: true,
        message: "Operator profile successfully initialized.",
        user: {
          id: `op-${Date.now()}`,
          firstName,
          lastName,
          email,
        },
      },
      { status: 201 },
    )
  } catch (error) {
    console.error("[v0] Registration error:", error)
    return NextResponse.json(
      {
        success: false,
        message: "Internal server error during registration.",
      },
      { status: 500 },
    )
  }
}
