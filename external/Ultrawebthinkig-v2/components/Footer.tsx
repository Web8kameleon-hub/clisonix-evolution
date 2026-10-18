// components/Footer.tsx
import React from "react";
import styles from "./Footer.module.css";

const Footer = () => {
  return (
    <footer className={styles.footer}>
      <div className={styles.brand}>
        Ultrawebthinking © 2025 – Beyond Imagination
      </div>

      <div className={styles.links}>
        <a
          href="https://github.com/Web8kameleon-hub"
          target="_blank"
          rel="noopener noreferrer"
          className={styles.link}
        >
          GitHub
        </a>
        <a
          href="https://linkedin.com"
          target="_blank"
          rel="noopener noreferrer"
          className={styles.link}
        >
          LinkedIn
        </a>
        <a
          href="https://youtube.com"
          target="_blank"
          rel="noopener noreferrer"
          className={styles.link}
        >
          YouTube
        </a>
      </div>

      <div className={styles.version}>
        Version 1.0 – Krijuar me pasion & logjikë të pastër
      </div>
    </footer>
  );
};

// Removed default export: Footer;

