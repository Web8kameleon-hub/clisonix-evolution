/**
 * 🔐 ASI Authentication & Token Management
 * JWT-based access control for Cube.js API
 * 
 * @version 1.0.0
 * @author Ledjan Ahmati <dealsjona@gmail.com>
 */

export interface UserRole {
  role: 'admin' | 'user' | 'viewer';
  permissions: string[];
  userId: string;
  email?: string;
}

/**
 * 🎯 Dynamic Access Token Generator
 */
export function getAccessToken(): string {
  // In production, this would validate JWT from session/cookie
  if (typeof window === 'undefined') {
    return process.env.CUBEJS_API_SECRET || 'asi-cube-secret-key-2025';
  }

  // Client-side token generation
  try {
    const user = getCurrentUser();
    if (!user) {
      return process.env.NEXT_PUBLIC_CUBEJS_TOKEN || 'asi-cube-secret-key-2025';
    }

    // Generate role-based token
    return generateRoleBasedToken(user);
  } catch (error) {
    console.warn('Token generation failed:', error);
    return process.env.NEXT_PUBLIC_CUBEJS_TOKEN || 'asi-cube-secret-key-2025';
  }
}

/**
 * 👤 Get Current User from Session
 */
export function getCurrentUser(): UserRole | null {
  if (typeof window === 'undefined') return null;

  try {
    // Check localStorage for user session
    const userSession = localStorage.getItem('asi_user_session');
    if (userSession) {
      return JSON.parse(userSession);
    }

    // Check sessionStorage as fallback
    const sessionUser = sessionStorage.getItem('asi_current_user');
    if (sessionUser) {
      return JSON.parse(sessionUser);
    }

    // Default development user
    return {
      role: 'admin',
      permissions: ['analytics:read', 'analytics:write', 'forecast:access'],
      userId: 'dev_user_001',
      email: 'dealsjona@gmail.com'
    };
  } catch (error) {
    console.warn('User session parsing failed:', error);
    return null;
  }
}

/**
 * 🎫 Generate Role-Based Access Token
 */
function generateRoleBasedToken(user: UserRole): string {
  // In production, this would be a proper JWT
  const payload = {
    userId: user.userId,
    role: user.role,
    permissions: user.permissions,
    timestamp: Date.now(),
    expires: Date.now() + (24 * 60 * 60 * 1000) // 24 hours
  };

  // Simple base64 encoding for development
  const token = btoa(JSON.stringify(payload));
  return `ASI_${token}`;
}

/**
 * 🔍 Validate User Permission
 */
export function hasPermission(permission: string): boolean {
  const user = getCurrentUser();
  if (!user) return false;

  // Admin has all permissions
  if (user.role === 'admin') return true;

  // Check specific permission
  return user.permissions.includes(permission);
}

/**
 * 🚪 Set User Session
 */
export function setUserSession(user: UserRole): void {
  if (typeof window === 'undefined') return;

  try {
    localStorage.setItem('asi_user_session', JSON.stringify(user));
    sessionStorage.setItem('asi_current_user', JSON.stringify(user));
  } catch (error) {
    console.warn('Failed to set user session:', error);
  }
}

/**
 * 🚪 Clear User Session
 */
export function clearUserSession(): void {
  if (typeof window === 'undefined') return;

  try {
    localStorage.removeItem('asi_user_session');
    sessionStorage.removeItem('asi_current_user');
  } catch (error) {
    console.warn('Failed to clear user session:', error);
  }
}
