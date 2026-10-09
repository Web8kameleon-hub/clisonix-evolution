/**
 * Developer Documentation Redirect
 * Redirects to the main /developers page with 37 Live Endpoints
 */

"use client";

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function DeveloperDocsRedirect() {
  const router = useRouter();
  useEffect(() => {
    router.replace('/developers');
  }, [router]);
  return null;
}
