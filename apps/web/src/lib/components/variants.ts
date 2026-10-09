import { cva, type VariantProps } from 'class-variance-authority';

export const asiButton = cva(
  'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed',
  {
    variants: {
      variant: {
        default:
          'bg-neutral-900 text-slate-50 hover:bg-neutral-800 focus-visible:ring-neutral-900',
        destructive:
          'bg-red-600 text-slate-50 hover:bg-red-700 focus-visible:ring-red-600',
        outline:
          'border border-slate-200 bg-white hover:bg-slate-100 focus-visible:ring-neutral-900',
        secondary:
          'bg-slate-100 text-neutral-900 hover:bg-slate-200 focus-visible:ring-neutral-900',
        ghost: 'hover:bg-slate-100 focus-visible:ring-neutral-900',
        link: 'text-neutral-900 underline-offset-4 hover:underline focus-visible:ring-neutral-900',
      },
      size: {
        default: 'h-10 px-4 py-2',
        sm: 'h-9 rounded-md px-3 text-xs',
        lg: 'h-11 rounded-md px-8',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
);

export const commandInputVariants = cva(
  'flex items-center gap-2 px-4 py-3 bg-neutral-900 border border-neutral-700 rounded-lg font-mono text-sm text-slate-50 placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition-all',
  {
    variants: {
      state: {
        default: 'bg-neutral-900',
        focused: 'bg-neutral-800 ring-2 ring-violet-500',
        error: 'bg-red-950 ring-2 ring-red-500',
      },
    },
    defaultVariants: {
      state: 'default',
    },
  }
);

export const statusBadge = cva(
  'inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold transition-colors',
  {
    variants: {
      status: {
        active: 'bg-green-100 text-green-800',
        inactive: 'bg-gray-100 text-gray-800',
        warning: 'bg-yellow-100 text-yellow-800',
        error: 'bg-red-100 text-red-800',
        processing: 'bg-violet-100 text-neutral-800',
      },
      size: {
        default: 'px-3 py-1 text-xs',
        sm: 'px-2 py-0.5 text-xs',
        md: 'px-3 py-1.5 text-sm',
        lg: 'px-4 py-2 text-sm',
      },
    },
    defaultVariants: {
      status: 'inactive',
      size: 'default',
    },
  }
);

export const progressBar = cva(
  'w-full bg-gray-200 rounded-full h-2.5',
  {
    variants: {
      size: {
        default: 'h-2.5',
        sm: 'h-2',
        md: 'h-3',
        lg: 'h-4',
      },
    },
    defaultVariants: {
      size: 'default',
    },
  }
);

export const progressBarFill = cva(
  'bg-violet-600 h-2.5 rounded-full transition-all duration-300',
  {
    variants: {
      color: {
        default: 'bg-violet-600',
        success: 'bg-green-600',
        warning: 'bg-yellow-600',
        error: 'bg-red-600',
      },
    },
    defaultVariants: {
      color: 'default',
    },
  }
);

export type ASIButtonVariants = VariantProps<typeof asiButton>;
export type CommandInputVariants = VariantProps<typeof commandInputVariants>;
export type StatusBadgeVariants = VariantProps<typeof statusBadge>;
export type ProgressBarVariants = VariantProps<typeof progressBar>;
export type ProgressBarFillVariants = VariantProps<typeof progressBarFill>;
