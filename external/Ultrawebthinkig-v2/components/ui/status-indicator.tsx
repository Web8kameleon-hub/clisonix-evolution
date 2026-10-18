/**
 * 🎯 STATUS INDICATOR COMPONENT
 * CVA-powered status indicators for the cyber security dashboard
 */

import { motion } from 'framer-motion';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../../lib/utils';

const statusIndicatorVariants = cva(
  "flex items-center justify-center rounded-full transition-all duration-300",
  {
    variants: {
      size: {
        sm: "w-2 h-2",
        md: "w-3 h-3", 
        lg: "w-4 h-4",
        xl: "w-6 h-6"
      },
      status: {
        online: "bg-green-500 shadow-lg shadow-green-500/50",
        warning: "bg-yellow-500 shadow-lg shadow-yellow-500/50 animate-pulse",
        error: "bg-red-500 shadow-lg shadow-red-500/50 animate-pulse",
        offline: "bg-gray-500 shadow-lg shadow-gray-500/50",
        maintenance: "bg-blue-500 shadow-lg shadow-blue-500/50",
        critical: "bg-purple-600 shadow-lg shadow-purple-600/50 animate-bounce"
      },
      variant: {
        solid: "",
        outline: "bg-transparent border-2",
        pulse: "animate-ping"
      }
    },
    compoundVariants: [
      {
        status: "online",
        variant: "outline",
        class: "border-green-500 bg-green-500/20"
      },
      {
        status: "warning", 
        variant: "outline",
        class: "border-yellow-500 bg-yellow-500/20"
      },
      {
        status: "error",
        variant: "outline", 
        class: "border-red-500 bg-red-500/20"
      },
      {
        status: "offline",
        variant: "outline",
        class: "border-gray-500 bg-gray-500/20"
      }
    ],
    defaultVariants: {
      size: "md",
      status: "online",
      variant: "solid"
    }
  }
);

interface StatusIndicatorProps extends VariantProps<typeof statusIndicatorVariants> {
  className?: string;
  animate?: boolean;
  label?: string;
}

export function StatusIndicator({ 
  className, 
  size, 
  status, 
  variant, 
  animate = true,
  label,
  ...props 
}: StatusIndicatorProps) {
  const Component = animate ? motion.div : 'div';
  
  return (
    <div className="flex items-center gap-2">
      <Component
        className={cn(statusIndicatorVariants({ size, status, variant, className }))}
        {...(animate && {
          whileHover: { scale: 1.2 },
          transition: { type: "spring", stiffness: 400, damping: 17 }
        })}
        {...props}
      />
      {label && (
        <span className="text-sm text-slate-300">{label}</span>
      )}
    </div>
  );
}

export { statusIndicatorVariants };
