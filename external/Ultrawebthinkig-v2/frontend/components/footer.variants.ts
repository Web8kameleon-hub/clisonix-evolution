// frontend/components/footer.variants.ts
import { cva } from "class-variance-authority";

export const footer = cva(
  "w-full px-6 py-4 flex flex-col md:flex-row justify-between items-center border-t text-center gap-4 font-sans",
  {
    variants: {
      theme: {
        light: "bg-[#f8f9fa] text-[#333] border-[#e9ecef]",
        dark: "bg-[#0f172a] text-[#f8fafc] border-[#1e293b]",
      },
    },
    defaultVariants: {
      theme: "light",
    },
  }
);

export const link = cva(
  "text-sm font-medium transition-colors duration-200 hover:underline",
  {
    variants: {
      theme: {
        light: "text-[#007bff] hover:text-[#0056b3]",
        dark: "text-[#94a3b8] hover:text-[#38bdf8]",
      },
    },
    defaultVariants: {
      theme: "light",
    },
  }
);
