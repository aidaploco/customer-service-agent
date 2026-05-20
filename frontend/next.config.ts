import type { NextConfig } from 'next'

// SECURITY: GHSA-qx2v-qp2m-jg93 — PostCSS vulnerability in Next.js internal dependency.
// Not exploitable in our static CSS build context, but monitor for Next.js >= 16.3.0
// which is expected to resolve this. Run `npm audit` after upgrading to verify.
const nextConfig: NextConfig = {
  output: 'standalone',
}

export default nextConfig
