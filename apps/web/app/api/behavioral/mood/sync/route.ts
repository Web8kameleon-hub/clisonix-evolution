import { NextRequest, NextResponse } from 'next/server';

/**
 * Mood Journal Sync API
 * Syncs mood entries with backend and returns computed stats
 */

interface MoodEntry {
  id: string;
  mood: number;
  emoji: string;
  note: string;
  timestamp: string;
  timeOfDay: 'morning' | 'afternoon' | 'evening' | 'night';
  factors: string[];
}

interface SyncRequest {
  entries: MoodEntry[];
  deviceId: string;
  timezone: string;
}

export async function POST(request: NextRequest) {
  try {
    const body: SyncRequest = await request.json();
    const { entries = [], deviceId, timezone } = body;

    // Calculate stats from entries
    const stats = calculateMoodStats(entries);

    // In production, you would sync to database here
    // For now, just compute and return stats

    return NextResponse.json({
      success: true,
      synced: entries.length,
      deviceId,
      timezone,
      stats,
      serverTime: new Date().toISOString(),
      message: 'Mood data synced successfully'
    });

  } catch (error) {
    console.error('[Mood Sync API] Error:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to sync mood data',
        stats: null 
      },
      { status: 500 }
    );
  }
}

function calculateMoodStats(entries: MoodEntry[]) {
  if (!entries || entries.length === 0) {
    return {
      avgMood: 0,
      totalEntries: 0,
      streak: 0,
      bestTimeOfDay: 'morning',
      topFactors: [],
      trend: 'stable' as const
    };
  }

  // Average mood
  const avgMood = entries.reduce((sum, e) => sum + e.mood, 0) / entries.length;

  // Calculate streak
  let streak = 0;
  const sortedDates = [...new Set(entries.map(e => new Date(e.timestamp).toDateString()))].sort().reverse();
  const today = new Date();
  
  for (let i = 0; i < sortedDates.length; i++) {
    const expected = new Date(today);
    expected.setDate(expected.getDate() - i);
    if (sortedDates[i] === expected.toDateString()) {
      streak++;
    } else {
      break;
    }
  }

  // Best time of day
  const timeOfDayMoods: Record<string, { sum: number; count: number }> = {};
  entries.forEach(e => {
    if (!timeOfDayMoods[e.timeOfDay]) {
      timeOfDayMoods[e.timeOfDay] = { sum: 0, count: 0 };
    }
    timeOfDayMoods[e.timeOfDay].sum += e.mood;
    timeOfDayMoods[e.timeOfDay].count++;
  });

  let bestTimeOfDay = 'morning';
  let bestAvg = 0;
  Object.entries(timeOfDayMoods).forEach(([time, data]) => {
    const avg = data.sum / data.count;
    if (avg > bestAvg) {
      bestAvg = avg;
      bestTimeOfDay = time;
    }
  });

  // Top factors
  const factorCounts: Record<string, number> = {};
  entries.forEach(e => {
    e.factors?.forEach(f => {
      factorCounts[f] = (factorCounts[f] || 0) + 1;
    });
  });
  const topFactors = Object.entries(factorCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3)
    .map(([factor]) => factor);

  // Trend (compare last 7 days to previous 7 days)
  const now = Date.now();
  const week = 7 * 24 * 60 * 60 * 1000;
  const recentEntries = entries.filter(e => now - new Date(e.timestamp).getTime() < week);
  const olderEntries = entries.filter(e => {
    const age = now - new Date(e.timestamp).getTime();
    return age >= week && age < 2 * week;
  });

  let trend: 'improving' | 'stable' | 'declining' = 'stable';
  if (recentEntries.length > 0 && olderEntries.length > 0) {
    const recentAvg = recentEntries.reduce((s, e) => s + e.mood, 0) / recentEntries.length;
    const olderAvg = olderEntries.reduce((s, e) => s + e.mood, 0) / olderEntries.length;
    if (recentAvg - olderAvg > 0.3) trend = 'improving';
    else if (olderAvg - recentAvg > 0.3) trend = 'declining';
  }

  return {
    avgMood: Math.round(avgMood * 10) / 10,
    totalEntries: entries.length,
    streak,
    bestTimeOfDay,
    topFactors,
    trend
  };
}

// GET endpoint for fetching mood data
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const deviceId = searchParams.get('deviceId');

  return NextResponse.json({
    success: true,
    deviceId,
    entries: [], // Would fetch from database in production
    message: 'Mood data retrieved successfully'
  });
}
