export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  message?: string;
}

export function createResponse<T>(data: T): ApiResponse<T> {
  return { data };
}

export function createErrorResponse(error: string): ApiResponse {
  return { error };
}

export function formatDate(date: Date): string {
  return date.toISOString().split('T')[0];
}
