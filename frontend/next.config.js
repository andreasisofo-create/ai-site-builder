/** @type {import('next').NextConfig} */
const nextConfig = {
  // Directory di output per Vercel
  distDir: '.next',

  // Immagini ottimizzate
  images: {
    unoptimized: true,
  },

  // Rewrites per API
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    return [
      {
        // Escludi le rotte di NextAuth dal proxy verso il backend
        source: '/api/((?!auth).*)',
        destination: `${apiUrl}/api/:path*`,
      },
    ];
  },

  // Headers per sicurezza
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
        ],
      },
    ];
  },

  // Trailing slash per SEO
  trailingSlash: false,

  // Compressione
  compress: true,
};

module.exports = nextConfig;
