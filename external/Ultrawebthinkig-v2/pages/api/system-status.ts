/**
 * System Status API - Real-time metrics from Clisonix
 * NO MOCK DATA - LIVE PRODUCTION ENDPOINTS
 */

import type { NextApiRequest, NextApiResponse } from 'next';

const CLISONIX_URL = process.env.NEXT_PUBLIC_CLISONIX_URL || 'https://clisonix.com';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // Fetch real system status from Clisonix
    const response = await fetch(`${CLISONIX_URL}/api/system-status`);
    
    if (!response.ok) {
      throw new Error(`Clisonix error: ${response.status}`);
    }

    const data = await response.json();
    
    // Transform to UltraWeb format
    return res.status(200).json({
      success: true,
      source: 'clisonix-cloud',
      timestamp: new Date().toISOString(),
      data: {
        status: data.data?.status || 'active',
        uptime: data.data?.uptime || 'N/A',
        instance_id: data.data?.instance_id || 'unknown',
        system: {
          cpu: data.data?.system?.cpu_percent || 0,
          memory: data.data?.system?.memory_percent || 0,
          disk: data.data?.system?.disk_percent || 0,
          processes: data.data?.system?.processes || 0,
          hostname: data.data?.system?.hostname || 'unknown'
        },
        services: {
          redis: data.data?.redis?.status || 'not_configured',
          database: data.data?.database?.status || 'not_configured',
          api: 'operational'
        }
      }
    });

  } catch (error) {
    console.error('System status error:', error);
    
    return res.status(200).json({
      success: false,
      source: 'fallback',
      timestamp: new Date().toISOString(),
      data: {
        status: 'checking',
        uptime: 'N/A',
        message: 'Connecting to Clisonix Cloud...'
      }
    });
  }
}
