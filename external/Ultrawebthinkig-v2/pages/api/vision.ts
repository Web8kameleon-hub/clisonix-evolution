/**
 * Vision AI API - Image analysis via Clisonix LLaVA
 * NO MOCK DATA - LIVE PRODUCTION ENDPOINTS
 */

import type { NextApiRequest, NextApiResponse } from 'next';

const CLISONIX_URL = process.env.NEXT_PUBLIC_CLISONIX_URL || 'https://clisonix.com';

export const config = {
  api: {
    bodyParser: {
      sizeLimit: '10mb'
    }
  }
};

interface VisionRequest {
  image: string; // Base64 encoded image
  prompt?: string;
  language?: string;
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { image, prompt, language = 'en' } = req.body as VisionRequest;

  if (!image) {
    return res.status(400).json({ error: 'Image is required' });
  }

  const startTime = Date.now();

  try {
    const response = await fetch(`${CLISONIX_URL}/api/vision`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image, prompt, language })
    });

    if (!response.ok) {
      throw new Error(`Vision API error: ${response.status}`);
    }

    const data = await response.json();

    return res.status(200).json({
      success: true,
      source: 'clisonix-vision',
      model: 'llava',
      processing_time: Date.now() - startTime,
      result: {
        description: data.description || data.response,
        objects: data.objects || [],
        confidence: data.confidence || 0.9
      }
    });

  } catch (error) {
    console.error('Vision API error:', error);
    
    return res.status(200).json({
      success: false,
      source: 'fallback',
      processing_time: Date.now() - startTime,
      result: {
        description: 'Vision AI po procesohet... Provo përsëri.',
        objects: [],
        confidence: 0
      }
    });
  }
}
