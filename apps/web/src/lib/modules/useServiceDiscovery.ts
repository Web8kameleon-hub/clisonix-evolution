'use client';

import { useEffect, useState } from 'react';
import type { ServiceState } from '../orchestration-topology';

export interface DiscoveredService {
  id: string;
  name: string;
  category: string;
  capabilities: string[];
  state?: ServiceState;
  latencyMs?: number;
  checkedAt?: string;
}

interface ServiceDiscoveryState {
  services: DiscoveredService[];
  loading: boolean;
  error: string | null;
  source: 'registry' | 'catalog' | null;
  updatedAt: string | null;
}

const INITIAL_STATE: ServiceDiscoveryState = {
  services: [],
  loading: true,
  error: null,
  source: null,
  updatedAt: null,
};

/**
 * Fetches the real, live service topology from /api/service-discovery
 * (docker-compose + registry + health probes). No fabricated status —
 * a module with no matching service simply gets no state.
 */
export function useServiceDiscovery(pollMs = 30000): ServiceDiscoveryState {
  const [state, setState] = useState<ServiceDiscoveryState>(INITIAL_STATE);

  useEffect(() => {
    let active = true;

    const load = async () => {
      try {
        const response = await fetch('/api/service-discovery', { cache: 'no-store' });
        if (!response.ok) {
          throw new Error(`service-discovery responded ${response.status}`);
        }

        const payload = await response.json();
        if (!active) return;

        const services: DiscoveredService[] = Array.isArray(payload?.data?.services)
          ? payload.data.services
          : [];

        setState({
          services,
          loading: false,
          error: null,
          source: payload?.meta?.source === 'registry' ? 'registry' : 'catalog',
          updatedAt: typeof payload?.meta?.timestamp === 'string' ? payload.meta.timestamp : null,
        });
      } catch (err) {
        if (!active) return;
        setState((prev) => ({
          ...prev,
          services: prev.services.map((service) => ({ ...service, state: 'unknown' })),
          loading: false,
          error: err instanceof Error ? err.message : 'Service discovery unavailable',
        }));
      }
    };

    load();
    const interval = setInterval(load, pollMs);
    return () => {
      active = false;
      clearInterval(interval);
    };
  }, [pollMs]);

  return state;
}

/**
 * Matches a module's mapped service id (from platform-map.ts) against the
 * live discovery list, falling back to a capability-name match. Returns
 * undefined (not "unknown"/"live") when nothing real is monitoring it yet,
 * so the UI can honestly say "Not monitored" instead of guessing.
 */
export function findServiceForModule(
  serviceId: string | undefined,
  services: DiscoveredService[],
): DiscoveredService | undefined {
  if (!serviceId || services.length === 0) return undefined;
  const normalized = serviceId.trim().toLowerCase();

  return (
    services.find((service) => service.id.toLowerCase() === normalized) ||
    services.find((service) =>
      service.capabilities.some((capability) => capability.toLowerCase() === normalized),
    )
  );
}
