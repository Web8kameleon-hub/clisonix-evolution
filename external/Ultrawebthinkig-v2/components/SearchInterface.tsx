import React from "react";
import { css } from "..//css";

const styles = {
  container: css({
    display: "flex",
    gap: "4",
    marginBottom: "6",
  }),
  input: css({
    flex: 1,
    padding: "3",
    border: "1px solid",
    borderColor: "gray.300",
    borderRadius: "md",
    fontSize: "md",
  }),
  button: css({
    bg: "blue.600",
    color: "white",
    paddingX: "4",
    borderRadius: "md",
    fontWeight: "bold",
    _hover: {
      bg: "blue.700",
    },
  }),
};

const SearchInterface: React.FC = () => {
  return (
    <div className={styles.container}>
      <input
        type="text"
        placeholder="Kërko në Web8..."
        className={styles.input}
      />
      <button className={styles.button}>Kërko</button>
    </div>
  );
};

// Removed default export: SearchInterface;
