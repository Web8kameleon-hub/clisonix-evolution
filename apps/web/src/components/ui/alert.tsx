import React from 'react'
import { cn } from '@/lib/utils'
import { AlertTriangle, CheckCircle, Info, X, AlertCircle } from 'lucide-react'

interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'destructive' | 'warning' | 'success' | 'info'
  title?: string
  dismissible?: boolean
  onDismiss?: () => void
}

const Alert = React.forwardRef<HTMLDivElement, AlertProps>(
  ({ className, variant = 'default', title, dismissible = false, onDismiss, children, ...props }, ref) => {
    const variants = {
      default: 'border-gray-200 bg-gray-50 text-gray-800',
      destructive: 'border-red-200 bg-red-50 text-red-800',
      warning: 'border-orange-200 bg-orange-50 text-orange-800',
      success: 'border-green-200 bg-green-50 text-green-800',
      info: 'border-violet-200 bg-violet-50 text-neutral-800'
    }

    const icons = {
      default: Info,
      destructive: AlertCircle,
      warning: AlertTriangle,
      success: CheckCircle,
      info: Info
    }

    const Icon = icons[variant]

    return (
      <div
        ref={ref}
        role="alert"
        className={cn(
          'relative rounded-lg border px-4 py-3 text-sm',
          variants[variant],
          className
        )}
        {...props}
      >
        <div className="flex items-start gap-3">
          <Icon className="h-4 w-4 mt-0.5 flex-shrink-0" />
          <div className="flex-1">
            {title && (
              <h5 className="font-medium mb-1">{title}</h5>
            )}
            <div>{children}</div>
          </div>
          {dismissible && onDismiss && (
            <button
              onClick={onDismiss}
              className="flex-shrink-0 opacity-70 hover:opacity-100 transition-opacity"
              title="Dismiss alert"
              aria-label="Dismiss alert"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>
    )
  }
)

Alert.displayName = 'Alert'

const AlertDescription = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("text-sm [&_p]:leading-relaxed", className)}
    {...props}
  />
))
AlertDescription.displayName = "AlertDescription"

const AlertTitle = React.forwardRef<
  HTMLHeadingElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h5
    ref={ref}
    className={cn("mb-1 font-medium leading-none tracking-tight", className)}
    {...props}
  />
))
AlertTitle.displayName = "AlertTitle"

export { Alert, AlertDescription, AlertTitle }

