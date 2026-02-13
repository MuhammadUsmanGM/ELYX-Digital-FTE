import { createClient } from '@supabase/supabase-js'
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export async function middleware(req: NextRequest) {
  const res = NextResponse.next()
  
  const { pathname } = req.nextUrl

  // Protect all dashboard and internal routes
  // Allow access to /auth, /api, and static assets
  const isAuthPage = pathname.startsWith('/auth')
  const isApiRoute = pathname.startsWith('/api')
  const isPublicFile = pathname.includes('.') // Simple check for assets
  const isStaticNext = pathname.startsWith('/_next')

  // Extract session from cookies
  const cookieHeader = req.headers.get('cookie') || ''
  const cookies = cookieHeader.split(';').reduce((acc, cookie) => {
    const [key, value] = cookie.trim().split('=')
    if (key && value) acc[key] = decodeURIComponent(value)
    return acc
  }, {} as Record<string, string>)

  // Check for Supabase auth token in cookies
  const authToken = cookies['sb-' + (process.env.NEXT_PUBLIC_SUPABASE_URL?.split('//')[1]?.split('.')[0] || 'localhost') + '-auth-token']
  const hasSession = !!authToken && authToken !== 'null' && authToken !== 'undefined'

  if (!hasSession && !isAuthPage && !isApiRoute && !isPublicFile && !isStaticNext && pathname !== '/') {
    return NextResponse.redirect(new URL('/auth', req.url))
  }

  // If logged in and on auth page, redirect to dashboard
  if (hasSession && isAuthPage) {
    return NextResponse.redirect(new URL('/dashboard', req.url))
  }

  return res
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
}
