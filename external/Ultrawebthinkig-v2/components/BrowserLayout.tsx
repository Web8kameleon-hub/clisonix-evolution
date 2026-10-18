import React from "react";

interface BrowserLayoutProps {
  children: React.ReactNode;
}

export function BrowserLayout({ children }: BrowserLayoutProps) {
  return (
    <div style={{ border: "2px solid #ccc", padding: "1rem", borderRadius: "1rem" }}>
      {children}
    </div>
  );
}


