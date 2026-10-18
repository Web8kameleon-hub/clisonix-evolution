import React from "react";

const Navbar: React.FC = () => {
  return (
    <nav
      style={{
        position: "sticky",
        top: 0,
        zIndex: 100,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        padding: "20px 32px",
        background: "rgba(70, 130, 180, 0.15)",
        backdropFilter: "blur(20px)",
        borderBottom: "2px solid rgba(70, 130, 180, 0.3)",
        boxShadow: "0 2px 8px rgba(0, 0, 0, 0.1)",
      }}
    >
      <div
        style={{
          fontSize: "24px",
          fontWeight: "400",
          color: "#1e90ff",
          letterSpacing: "2px",
          textAlign: "center",
          fontFamily: "'Inter', 'Helvetica Neue', sans-serif",
          textShadow: "0 1px 2px rgba(0, 0, 0, 0.1)",
        }}
      >
        ultrawebthinking
      </div>
    </nav>
  );
};

// Removed default export: Navbar;
