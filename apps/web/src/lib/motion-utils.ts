import { cva } from "class-variance-authority";

// Utility function for combining classes
export function cn(...inputs: (string | undefined | null | false)[]): string {
  return inputs.filter(Boolean).join(" ");
}

// Animation variants for Framer Motion
export const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 }
};

export const scaleIn = {
  initial: { opacity: 0, scale: 0.8 },
  animate: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.8 }
};

export const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.1
    }
  }
};

export const staggerItem = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 }
};

// Glow effects for agents
export const albaGlow = {
  boxShadow: "0 0 20px rgba(14, 165, 233, 0.3)"
};

export const jonaGlow = {
  boxShadow: "0 0 20px rgba(139, 92, 246, 0.3)"
};

// Button variants
export const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed",
  {
    variants: {
      variant: {
        default: "bg-neutral-900 text-slate-50 hover:bg-neutral-800",
        destructive: "bg-red-600 text-slate-50 hover:bg-red-700",
        outline: "border border-slate-200 bg-white hover:bg-slate-100",
        secondary: "bg-slate-100 text-neutral-900 hover:bg-slate-200",
        ghost: "hover:bg-slate-100",
        link: "text-neutral-900 underline-offset-4 hover:underline",
        alba: "bg-violet-600 text-white hover:bg-violet-700 focus-visible:ring-violet-600",
        jona: "bg-purple-600 text-white hover:bg-purple-700 focus-visible:ring-purple-600",
        harmony: "bg-gradient-to-r from-violet-600 to-purple-600 text-white hover:from-violet-700 hover:to-purple-700",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);
