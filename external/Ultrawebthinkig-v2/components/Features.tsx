// components/Features.tsx
import React from "react";
import { Zap, ShieldCheck, Globe, Brain } from "lucide-react";
import styles from "./Features.module.css";

const features = [
  {
    icon: <Zap size={32} strokeWidth={2.5} />,
    title: "Shpejtësi Ekstreme",
    desc: "Arkitekturë ultra-performante për ngarkim të menjëhershëm.",
  },
  {
    icon: <ShieldCheck size={32} strokeWidth={2.5} />,
    title: "Siguri Absolute",
    desc: "Mbrojtje me firewall inteligjent dhe enkriptim post-kuantik.",
  },
  {
    icon: <Globe size={32} strokeWidth={2.5} />,
    title: "Lidhje Globale",
    desc: "Dekentralizim i plotë me akses global satelitor dhe tokësor.",
  },
  {
    icon: <Brain size={32} strokeWidth={2.5} />,
    title: "Inteligjencë AGI",
    desc: "Zgjuarsi që mëson, parashikon dhe vepron përpara çdo nevoje.",
  },
];

const Features = () => {
  return (
    <section className={styles.section}>
      <div className={styles.titleBlock}>
        <h2 className={styles.title}>Teknologji e Ardhshme</h2>
        <p className={styles.subtitle}>
          Platform revolucionar që kombinon AGI, siguri post-kuantike dhe
          arkitekturë dekentralizuese për një përvojë të pakrahasueshme.
        </p>
      </div>

      <div className={styles.grid}>
        {features.map((feature, index) => (
          <div key={index} className={styles.card}>
            <div className={styles.icon}>{feature.icon}</div>
            <h3 className={styles.featureTitle}>{feature.title}</h3>
            <p className={styles.featureDesc}>{feature.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
};

// Removed default export: Features;

