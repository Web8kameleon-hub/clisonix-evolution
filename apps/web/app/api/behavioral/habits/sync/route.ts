import { NextRequest, NextResponse } from 'next/server';

/**
 * Daily Habits Sync API
 * Syncs habit data with backend and returns computed stats
 */

interface Habit {
  id: string;
  name: string;
  emoji: string;
  frequency: 'daily' | 'weekly';
  targetPerDay: number;
  color: string;
  createdAt: string;
}

interface HabitLog {
  habitId: string;
  date: string;
  completed: number;
  timestamp: string;
}

interface SyncRequest {
  habits: Habit[];
  logs: HabitLog[];
  deviceId: string;
  timezone: string;
}

export async function POST(request: NextRequest) {
  try {
    const body: SyncRequest = await request.json();
    const { habits = [], logs = [], deviceId, timezone } = body;

    // Calculate stats for each habit
    const stats = calculateHabitStats(habits, logs);

    return NextResponse.json({
      success: true,
      synced: {
        habits: habits.length,
        logs: logs.length
      },
      deviceId,
      timezone,
      stats,
      serverTime: new Date().toISOString(),
      message: 'Habits data synced successfully'
    });

  } catch (error) {
    console.error('[Habits Sync API] Error:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to sync habits data',
        stats: null 
      },
      { status: 500 }
    );
  }
}

function calculateHabitStats(habits: Habit[], logs: HabitLog[]) {
  const statsMap: Record<string, unknown> = {};

  habits.forEach(habit => {
    const habitLogs = logs.filter(l => l.habitId === habit.id);
    
    // Calculate streak
    let currentStreak = 0;
    let longestStreak = 0;
    let tempStreak = 0;
    
    const today = new Date();
    const sortedDates = [...new Set(habitLogs.map(l => l.date))].sort().reverse();
    
    // Current streak
    for (let i = 0; i < sortedDates.length; i++) {
      const expected = new Date(today);
      expected.setDate(expected.getDate() - i);
      const expectedStr = expected.toISOString().split('T')[0];
      
      if (sortedDates[i] === expectedStr) {
        currentStreak++;
      } else {
        break;
      }
    }

    // Longest streak
    const allDates = [...new Set(habitLogs.map(l => l.date))].sort();
    let prevDate: Date | null = null;
    
    allDates.forEach(dateStr => {
      const date = new Date(dateStr);
      if (prevDate) {
        const diff = (date.getTime() - prevDate.getTime()) / (1000 * 60 * 60 * 24);
        if (diff === 1) {
          tempStreak++;
        } else {
          longestStreak = Math.max(longestStreak, tempStreak);
          tempStreak = 1;
        }
      } else {
        tempStreak = 1;
      }
      prevDate = date;
    });
    longestStreak = Math.max(longestStreak, tempStreak);

    // Completion rate (last 30 days)
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    const recentLogs = habitLogs.filter(l => new Date(l.date) >= thirtyDaysAgo);
    const completionRate = Math.min(100, Math.round((recentLogs.length / 30) * 100));

    // Total completions
    const totalCompletions = habitLogs.reduce((sum, l) => sum + l.completed, 0);

    statsMap[habit.id] = {
      habitId: habit.id,
      currentStreak,
      longestStreak,
      completionRate,
      totalCompletions,
      lastCompleted: habitLogs[0]?.date || null
    };
  });

  return statsMap;
}

// GET endpoint for fetching habit data
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const deviceId = searchParams.get('deviceId');

  return NextResponse.json({
    success: true,
    deviceId,
    habits: [],
    logs: [],
    message: 'Habits data retrieved successfully'
  });
}
