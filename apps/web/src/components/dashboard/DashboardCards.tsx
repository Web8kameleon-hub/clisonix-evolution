'use client';

import { ReactNode } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { LucideIcon, TrendingUp, TrendingDown, Minus } from 'lucide-react';

// Stats Card Component
interface StatsCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon?: LucideIcon | string;
  trend?: {
    value: number;
    label?: string;
  };
  progress?: number;
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info';
  className?: string;
}

export function StatsCard({
  title,
  value,
  description,
  icon: Icon,
  trend,
  progress,
  variant = 'default',
  className,
}: StatsCardProps) {
  const variantStyles = {
    default: 'from-neutral-800/50 to-neutral-900/50 border-neutral-700/50',
    success: 'from-green-900/30 to-green-950/30 border-green-700/50',
    warning: 'from-yellow-900/30 to-yellow-950/30 border-yellow-700/50',
    danger: 'from-red-900/30 to-red-950/30 border-red-700/50',
    info: 'from-neutral-900/30 to-cyan-950/30 border-violet-700/50',
  };

  const valueColors = {
    default: 'text-white',
    success: 'text-green-400',
    warning: 'text-yellow-400',
    danger: 'text-red-400',
    info: 'text-violet-400',
  };



  const TrendIcon = trend 
    ? trend.value > 0 ? TrendingUp 
    : trend.value < 0 ? TrendingDown 
    : Minus
    : null;

  return (
    <Card className={cn(
      'bg-gradient-to-br border rounded-xl overflow-hidden',
      variantStyles[variant],
      className
    )}>
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-gray-400 text-sm font-medium">{title}</span>
          {Icon && (
            typeof Icon === 'string' ? (
              <span className="text-2xl">{Icon}</span>
            ) : (
              <Icon className="w-5 h-5 text-gray-400" />
            )
          )}
        </div>
        
        <div className="flex items-end gap-2">
          <span className={cn('text-3xl font-bold', valueColors[variant])}>
            {value}
          </span>
          {trend && TrendIcon && (
            <div className={cn(
              'flex items-center gap-1 text-xs font-medium mb-1',
              trend.value > 0 ? 'text-green-400' : trend.value < 0 ? 'text-red-400' : 'text-gray-400'
            )}>
              <TrendIcon className="w-3 h-3" />
              <span>{Math.abs(trend.value)}%</span>
            </div>
          )}
        </div>

        {description && (
          <p className="text-xs text-gray-500 mt-2">{description}</p>
        )}

        {progress !== undefined && (
          <div className="mt-4">
            <Progress 
              value={progress} 
              className="h-2 bg-neutral-700"
            />
          </div>
        )}

        {trend?.label && (
          <p className="text-xs text-gray-500 mt-2">{trend.label}</p>
        )}
      </CardContent>
    </Card>
  );
}

// Metric Item Component (for lists)
interface MetricItemProps {
  label: string;
  value: string | number;
  icon?: string;
  status?: 'online' | 'offline' | 'warning' | 'error';
  className?: string;
}

export function MetricItem({ label, value, icon, status, className }: MetricItemProps) {
  const statusColors = {
    online: 'text-green-400',
    offline: 'text-gray-400',
    warning: 'text-yellow-400',
    error: 'text-red-400',
  };

  return (
    <div className={cn(
      'flex justify-between items-center p-3 bg-neutral-900/50 rounded-lg',
      className
    )}>
      <div className="flex items-center gap-2">
        {icon && <span>{icon}</span>}
        <span className="text-gray-400">{label}</span>
      </div>
      <span className={cn('font-bold', status ? statusColors[status] : 'text-white')}>
        {value}
      </span>
    </div>
  );
}

// Status Badge Component
interface StatusBadgeProps {
  status: 'active' | 'inactive' | 'error' | 'pending' | 'online' | 'offline';
  label?: string;
  className?: string;
}

export function StatusBadge({ status, label, className }: StatusBadgeProps) {
  const statusConfig = {
    active: { color: 'bg-green-500/20 text-green-400 border-green-500/30', text: 'Active' },
    inactive: { color: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30', text: 'Inactive' },
    error: { color: 'bg-red-500/20 text-red-400 border-red-500/30', text: 'Error' },
    pending: { color: 'bg-gray-500/20 text-gray-300 border-gray-500/30', text: 'Pending' },
    online: { color: 'bg-green-500/20 text-green-400 border-green-500/30', text: 'Online' },
    offline: { color: 'bg-gray-500/20 text-gray-400 border-gray-500/30', text: 'Offline' },
  };

  const config = statusConfig[status];

  return (
    <Badge 
      variant="outline"
      className={cn('font-medium border', config.color, className)}
    >
      {label || config.text}
    </Badge>
  );
}

// Section Header Component
interface SectionHeaderProps {
  title: string;
  description?: string;
  icon?: string;
  action?: ReactNode;
  className?: string;
}

export function SectionHeader({ title, description, icon, action, className }: SectionHeaderProps) {
  return (
    <div className={cn('flex items-center justify-between mb-6', className)}>
      <div>
        <h2 className="text-xl font-bold flex items-center gap-2 text-white">
          {icon && <span>{icon}</span>}
          {title}
        </h2>
        {description && (
          <p className="text-gray-400 text-sm mt-1">{description}</p>
        )}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}

// Data Source Card Component
interface DataSourceCardProps {
  id: string;
  name: string;
  type: 'IOT' | 'API' | 'DATABASE' | 'WEBHOOK';
  status: 'active' | 'inactive' | 'error';
  lastSync?: string;
  dataPoints?: number;
  onClick?: () => void;
  className?: string;
}

export function DataSourceCard({
  name,
  type,
  status,
  lastSync,
  dataPoints,
  onClick,
  className,
}: DataSourceCardProps) {
  const typeIcons = {
    IOT: '📡',
    API: '🔗',
    DATABASE: '🗄️',
    WEBHOOK: '🪝',
  };

  return (
    <Card 
      className={cn(
        'bg-gradient-to-br from-neutral-800/50 to-neutral-900/50 border-neutral-700/50',
        'hover:border-violet-500/30 transition-all cursor-pointer',
        className
      )}
      onClick={onClick}
    >
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-2">
          <div className="flex items-center gap-3">
            <span className="text-2xl">{typeIcons[type]}</span>
            <div>
              <h3 className="font-semibold text-white">{name}</h3>
              <span className="text-xs text-gray-500">{type}</span>
            </div>
          </div>
          <StatusBadge status={status} />
        </div>
        {(lastSync || dataPoints !== undefined) && (
          <div className="text-xs text-gray-400 space-y-1 mt-3">
            {lastSync && <p>Last sync: {lastSync}</p>}
            {dataPoints !== undefined && <p>{dataPoints.toLocaleString()} points</p>}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Empty State Component
interface EmptyStateProps {
  icon?: string;
  title: string;
  description?: string;
  action?: ReactNode;
  className?: string;
}

export function EmptyState({ icon, title, description, action, className }: EmptyStateProps) {
  return (
    <div className={cn(
      'flex flex-col items-center justify-center py-12 px-4 text-center',
      className
    )}>
      {icon && <span className="text-5xl mb-4">{icon}</span>}
      <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
      {description && <p className="text-gray-400 mb-6 max-w-sm">{description}</p>}
      {action && action}
    </div>
  );
}

// Loading Skeleton for Stats
export function StatsCardSkeleton() {
  return (
    <Card className="bg-gradient-to-br from-neutral-800/50 to-neutral-900/50 border-neutral-700/50">
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-2">
          <div className="h-4 w-24 bg-neutral-700 rounded animate-pulse" />
          <div className="h-6 w-6 bg-neutral-700 rounded animate-pulse" />
        </div>
        <div className="h-9 w-20 bg-neutral-700 rounded animate-pulse mt-2" />
        <div className="h-3 w-32 bg-neutral-700 rounded animate-pulse mt-4" />
      </CardContent>
    </Card>
  );
}
