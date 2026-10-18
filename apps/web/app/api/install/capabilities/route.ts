export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET() {
  const twaUrl = (process.env.TWA_INSTALL_URL || '').trim();
  const twaPackage = (process.env.TWA_PACKAGE_ID || '').trim();
  return Response.json({
    version: 'install-capabilities-v1',
    pwa: {
      available: true,
      manifest: '/manifest.json',
      start_url: '/modules?source=pwa',
    },
    twa: {
      available: Boolean(twaUrl),
      url: twaUrl || null,
      package_id: twaPackage || null,
      start_url: '/modules?source=twa',
    },
  }, { headers: { 'Cache-Control': 'no-store' } });
}
