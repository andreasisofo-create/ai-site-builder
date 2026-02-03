/** @type {import('next').NextConfig} */
const nextConfig = {
  // Rimuoviamo output: 'standalone' per usare il default Vercel (serverless)
  // che supporta pagine dinamiche
  
  // Immagini ottimizzate
  images: {
    unoptimized: true,
  },
  
  // Rewrites per API
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    return [
      {
        source: '/api/:path*',
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
