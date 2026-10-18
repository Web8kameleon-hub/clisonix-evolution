// components/Explore.tsx
import { css } from "..//css";

export function Explore() {
  return (
    <section className={styles.section}>
      <h2 className={styles.heading}>Eksploro Dimensione të Reja</h2>
      <p className={styles.subtitle}>
        Me Ultrawebthinking, ti nuk shfleton thjesht uebin – ti eksploron një mendje kolektive.
      </p>
      <div className={styles.wrapper}>
        <a href="#" className={styles.card}>
          <h3 className={styles.cardTitle}>Navigim AGI</h3>
          <p className={styles.cardText}>
            Zbulim i zgjuar i përmbajtjes përmes analitikës dhe inteligjencës kolektive.
          </p>
        </a>
        <a href="#" className={styles.card}>
          <h3 className={styles.cardTitle}>Botë Paralele</h3>
          <p className={styles.cardText}>
            Qasje në shtresa të ndryshme informacioni për çdo realitet virtual ose fizik.
          </p>
        </a>
      </div>
    </section>
  );
}

const styles = {
  section: css({
    paddingY: "20",
    paddingX: "6",
    background: "white",
    textAlign: "center",
  }),
  heading: css({
    fontSize: "4xl",
    fontWeight: "bold",
    color: "blue.800",
    marginBottom: "4",
  }),
  subtitle: css({
    fontSize: "lg",
    color: "gray.600",
    maxWidth: "700px",
    margin: "0 auto",
    marginBottom: "10",
  }),
  wrapper: css({
    display: "flex",
    flexDirection: ["column", "row"],
    gap: "8",
    justifyContent: "center",
    flexWrap: "wrap",
  }),
  card: css({
    background: "blue.50",
    padding: "6",
    borderRadius: "xl",
    width: ["100%", "45%"],
    textAlign: "left",
    transition: "transform 0.3s ease, box-shadow 0.3s ease",
    _hover: {
      transform: "scale(1.03)",
      boxShadow: "xl",
    },
  }),
  cardTitle: css({
    fontSize: "xl",
    fontWeight: "semibold",
    color: "blue.700",
    marginBottom: "2",
  }),
  cardText: css({
    fontSize: "md",
    color: "gray.700",
  }),
};

