/**
 * User Routes Layout
 *
 * User auth-aware layout for authenticated routes
 * Keeps protected pages dynamic when they depend on session state
 *
 * @author Ledjan Ahmati
 * @copyright 2026 Clisonix Cloud
 */

// Skip pre-rendering for all user routes
export const dynamic = "force-dynamic";

import { ReactNode } from "react";

export default function UserLayout({
  children,
}: {
  children: ReactNode;
}) {
  return <>{children}</>;
}
