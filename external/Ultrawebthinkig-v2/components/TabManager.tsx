import React from "react";
import { css } from "..//css";

const styles = {
  wrapper: css({
    padding: "6",
    background: "white",
    borderRadius: "lg",
    boxShadow: "md",
    marginBottom: "6",
  }),
  title: css({
    fontSize: "2xl",
    fontWeight: "bold",
    color: "blue.700",
    marginBottom: "2",
  }),
  desc: css({
    fontSize: "md",
    color: "gray.700",
  }),
};

const TabManager: React.FC = () => {
  return (
    <div className={styles.wrapper}>
      <h2 className={styles.title}>Menaxhimi i Tabeve</h2>
      <p className={styles.desc}>
        Kaloni shpejt mes tabeve, projekteve dhe mendimeve me një ndërfaqe inteligjente.
      </p>
    </div>
  );
};

// Removed default export: TabManager;
