import { NextResponse } from 'next/server'

const BASE = process.env.API_BASE_URL ?? 'http://localhost:8000'

export async function GET() {
  try {
    const res = await fetch(`${BASE}/api/v1/agents`, { cache: 'no-store' })
    const data = await res.json()
    return NextResponse.json(data, { status: res.status })
  } catch {
    return NextResponse.json({ error: 'Backend unreachable' }, { status: 502 })
  }
}
