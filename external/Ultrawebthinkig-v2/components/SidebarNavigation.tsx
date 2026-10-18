import React from "react";

const SidebarNavigation: React.FC = () => {
  return (
    <aside style={{ width: "220px", background: "#f4f4f4", padding: "1rem" }}>
      <nav>
        <ul>
          <li><a href="#">Tabat</a></li>
          <li><a href="#">Historia</a></li>
          <li><a href="#">Favoritet</a></li>
          <li><a href="#">AI Qendrore</a></li>
        </ul>
      </nav>
    </aside>
  );
};

// Removed default export: SidebarNavigation;
