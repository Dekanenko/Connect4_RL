/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  // Allow backend URL to be configured at runtime
  env: {
    NEXT_PUBLIC_BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000/api',
  },
}

export default nextConfig
