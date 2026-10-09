"use client";

import { SessionProvider } from 'next-auth/react';
import { RequestLogger } from './telemetry/RequestLogger';

export default function AppProviders({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <RequestLogger />
      <SessionProvider refetchOnWindowFocus={false} refetchInterval={0}>
        {children}
      </SessionProvider>
    </>
  );
}
