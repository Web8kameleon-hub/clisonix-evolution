/**
 * Guardian Dashboard API
 * Real-time security monitoring and threat management
 * 
 * @version 8.0.0
 * @author Ledjan Ahmati
 * @contact dealsjona@gmail.com
 */

import { NextRequest, NextResponse } from 'next/server';
import { guardian } from '../../../backend/guardian/Guardian';

export async function GET() {
  try {
    const dashboard = guardian.getDashboard();
    
    return NextResponse.json({
      success: true,
      data: dashboard,
      timestamp: new Date().toISOString(),
      version: '8.0.0'
    });
  } catch (error) {
    console.error('Guardian dashboard error:', error);
    
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to fetch Guardian dashboard',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { action, ip, reason } = body;

    switch (action) {
      case 'block':
        if (!ip || !reason) {
          return NextResponse.json(
            { success: false, error: 'IP and reason required for blocking' },
            { status: 400 }
          );
        }
        guardian.manualBlockIP(ip, reason);
        return NextResponse.json({
          success: true,
          message: `IP ${ip} blocked successfully`,
          timestamp: new Date().toISOString()
        });

      case 'unblock':
        if (!ip) {
          return NextResponse.json(
            { success: false, error: 'IP required for unblocking' },
            { status: 400 }
          );
        }
        guardian.manualUnblockIP(ip);
        return NextResponse.json({
          success: true,
          message: `IP ${ip} unblocked successfully`,
          timestamp: new Date().toISOString()
        });

      case 'toggle':
        const { active } = body;
        guardian.setActive(active);
        return NextResponse.json({
          success: true,
          message: `Guardian ${active ? 'activated' : 'deactivated'}`,
          timestamp: new Date().toISOString()
        });

      default:
        return NextResponse.json(
          { success: false, error: 'Invalid action' },
          { status: 400 }
        );
    }
  } catch (error) {
    console.error('Guardian action error:', error);
    
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to execute Guardian action',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    );
  }
}
