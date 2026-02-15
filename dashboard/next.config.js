/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true,
    loader: 'akamai',
    path: '/',
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    NEXT_PUBLIC_VERSION: process.env.NEXT_PUBLIC_VERSION || '1.0.0',
  },
  // Note: headers, redirects, and rewrites are not supported with static export
  // These configurations are only used for server-side environments (Vercel, Node.js servers)
  // For static exports to GitHub Pages, these features are not applicable
}

module.exports = nextConfig
