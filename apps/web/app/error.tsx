'use client';

import { useEffect } from 'react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('Application error:', error);
  }, [error]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-white to-gray-100">
      <div className="text-center max-w-md px-4">
        <h1 className="text-6xl font-bold text-red-500 mb-4">Error</h1>
        <p className="text-xl text-gray-600 mb-4">Something went wrong!</p>
        <p className="text-sm text-gray-500 mb-8">{error.message}</p>
        <button
          onClick={reset}
          className="px-6 py-3 bg-violet-500 hover:bg-violet-600 text-white rounded-lg font-medium transition-colors"
        >
          Try again
        </button>
      </div>
    </div>
  );
}







