"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";

/**
 * ASI Main Content - Ultra SaaS Router
 * Simple redirect to Ultra SaaS Platform - Industrial Grade
 */
export default function ASIMainContent() {
  const router = useRouter();

  useEffect(() => {
    // Auto-redirect to Ultra SaaS Platform
    router.push("/ultra-saas");
  }, [router]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900">
      <div className="text-center space-y-4">
        <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-white mx-auto"></div>
        <h2 className="text-white text-xl font-semibold">🏭 Ultra SaaS Platform</h2>
        <p className="text-white/70">Redirecting to Ultra SaaS Dashboard...</p>
        <div className="mt-6">
          <a 
            href="/ultra-saas" 
            className="inline-block px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
          >
            Go to Ultra SaaS Platform →
          </a>
        </div>
      </div>
    </div>
  );
}
