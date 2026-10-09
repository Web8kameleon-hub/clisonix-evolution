import React from 'react'
import { cn } from '@/lib/utils'

interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  value?: number
  max?: number
  color?: 'blue' | 'green' | 'purple' | 'red' | 'orange' | 'yellow'
  size?: 'sm' | 'md' | 'lg'
  animated?: boolean
  showLabel?: boolean
  label?: string
}

const Progress = React.forwardRef<HTMLDivElement, ProgressProps>(
  ({ 
    className, 
    value = 0, 
    max = 100, 
    color = 'blue',
    size = 'md',
    animated = false,
    showLabel = false,
    label,
    ...props 
  }, ref) => {
    const percentage = Math.min(100, Math.max(0, (value / max) * 100))
    
    const colorClasses = {
      blue: 'bg-violet-600',
      green: 'bg-green-600',
      purple: 'bg-purple-600',
      red: 'bg-red-600',
      orange: 'bg-orange-600',
      yellow: 'bg-yellow-600'
    }

    const sizeClasses = {
      sm: 'h-1.5',
      md: 'h-2',
      lg: 'h-3'
    }

    return (
      <div ref={ref} className={cn('w-full', className)} {...props}>
        {showLabel && (
          <div className="flex justify-between text-xs text-muted-foreground mb-1">
            <span>{label}</span>
            <span>{percentage.toFixed(1)}%</span>
          </div>
        )}
        <div className={cn('w-full bg-gray-200 rounded-full overflow-hidden', sizeClasses[size])}>
          <div 
            className={cn(
              'h-full rounded-full transition-all duration-300 ease-in-out',
              colorClasses[color],
              animated && 'animate-pulse'
            )}
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>
    )
  }
)

Progress.displayName = 'Progress'

export { Progress }

