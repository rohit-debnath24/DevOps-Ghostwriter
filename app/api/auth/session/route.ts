import { NextResponse } from "next/server"

export async function GET() {
  // In a production app, this would check cookies/JWT tokens
  try {
    return NextResponse.json({
      authenticated: false,
      user: null,
    })
  } catch (error) {
    return NextResponse.json({ error: "Internal Server Error" }, { status: 500 })
  }
}
