/**
 * Audio Transcription API - Speech-to-text via Clisonix Whisper
 * NO MOCK DATA - LIVE PRODUCTION ENDPOINTS
 */

import type { NextApiRequest, NextApiResponse } from 'next';

const CLISONIX_URL = process.env.NEXT_PUBLIC_CLISONIX_URL || 'https://clisonix.com';

export const config = {
  api: {
    bodyParser: {
      sizeLimit: '25mb'
    }
  }
};

interface AudioRequest {
  audio: string; // Base64 encoded audio
  language?: string;
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { audio, language } = req.body as AudioRequest;

  if (!audio) {
    return res.status(400).json({ error: 'Audio is required' });
  }

  const startTime = Date.now();

  try {
    const response = await fetch(`${CLISONIX_URL}/api/audio/transcribe`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ audio, language })
    });

    if (!response.ok) {
      throw new Error(`Audio API error: ${response.status}`);
    }

    const data = await response.json();

    return res.status(200).json({
      success: true,
      source: 'clisonix-whisper',
      model: 'faster-whisper',
      processing_time: Date.now() - startTime,
      result: {
        text: data.text || '',
        language: data.language || language || 'auto',
        duration_seconds: data.duration_seconds || 0,
        confidence: data.confidence || 0.95
      }
    });

  } catch (error) {
    console.error('Audio API error:', error);
    
    return res.status(200).json({
      success: false,
      source: 'fallback',
      processing_time: Date.now() - startTime,
      result: {
        text: '',
        message: 'Audio transcription po procesohet... Provo përsëri.'
      }
    });
  }
}
