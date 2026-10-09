# DE + EN Claim Set (Working v1)

Document type: Bilingual claim drafting workspace
Jurisdiction focus: DE (DPMA) with EN parallel text for counsel workflow
Date: 2026-05-09

## Legal Note
This draft is technical support material and not legal advice. Final wording must be validated by a registered patent attorney.

## Independent Claims

### Claim 1 (Method)
DE: Computerimplementiertes Verfahren zur Sicherheitsklassifikation von Anfragen, umfassend: (i) Empfangen einer Anfrage mit Endpunktkennung, (ii) Erfassen eines Resonanzwertes in Nanodezibel, (iii) Fuhrung einer endpunktspezifischen Historie, (iv) Berechnung einer Baseline bei Erfullung einer Mindeststichprobe, (v) Ermittlung einer Abweichung zwischen Resonanzwert und Baseline, (vi) Zuordnung eines Schweregrades anhand mindestens zweier Nanodezibel-Schwellen, und (vii) Auswahl einer Laufzeitrichtlinie aus allow, monitor, throttle oder block.
EN: A computer-implemented method for request security classification comprising: (i) receiving a request with an endpoint identifier, (ii) obtaining a resonance value in nanodecibel units, (iii) maintaining endpoint-specific history, (iv) computing a baseline when a minimum sample condition is met, (v) determining deviation between resonance and baseline, (vi) assigning severity using at least two nanodecibel thresholds, and (vii) selecting a runtime policy from allow, monitor, throttle, or block.

### Claim 2 (System)
DE: System mit API-Laufzeitdienst, Sicherheitsmonitor, Lernkomponente und Richtlinien-Gate, eingerichtet zur Ausfuhrung des Verfahrens nach Anspruch 1.
EN: A system comprising an API runtime service, security monitor, learning component, and policy gate configured to perform the method of claim 1.

### Claim 3 (Computer Program Product)
DE: Nichtfluchtiges computerlesbares Medium mit Instruktionen, die bei Ausfuhrung das Verfahren nach Anspruch 1 bewirken.
EN: A non-transitory computer-readable medium storing instructions that, when executed, cause performance of the method of claim 1.

## Dependent Claims

### Claim 4
DE: Verfahren nach Anspruch 1, wobei die Baseline Mittelwert, Median und Standardabweichung in einem gleitenden Fenster umfasst.
EN: The method of claim 1, wherein the baseline includes mean, median, and standard deviation over a sliding window.

### Claim 5
DE: Verfahren nach Anspruch 1, wobei die Schweregradzuordnung zusatzlich einen Route-Match-Indikator umfasst.
EN: The method of claim 1, wherein severity assignment further uses a route-match indicator.

### Claim 6
DE: Verfahren nach Anspruch 1, wobei throttle eine konfigurierbare Verkehrsreduktionskomponente umfasst.
EN: The method of claim 1, wherein throttle includes a configurable traffic reduction factor.

### Claim 7
DE: Verfahren nach Anspruch 1, wobei ein negativer ndb_delta-Wert zur Risikodeeskalation genutzt wird.
EN: The method of claim 1, wherein a negative ndb_delta is used for risk de-escalation.

### Claim 8
DE: Verfahren nach Anspruch 1, wobei ein Tide-Zustand als zusatzliches Steuerungssignal fur Richtlinienumschaltung genutzt wird.
EN: The method of claim 1, wherein a tide state is used as an additional control signal for policy switching.

### Claim 9
DE: Verfahren nach Anspruch 1, wobei stigma_level die Freigabe von Endpunktaktionen steuert.
EN: The method of claim 1, wherein stigma_level controls endpoint action admission.

### Claim 10
DE: Verfahren nach Anspruch 1, wobei Ereignisse strukturierte Felder endpoint, action, stigma_level, ndb_score und outcome enthalten.
EN: The method of claim 1, wherein events contain structured fields endpoint, action, stigma_level, ndb_score, and outcome.

### Claim 11
DE: System nach Anspruch 2, wobei der Sicherheitsmonitor in einer Kernverarbeitungspipeline vor dem Ausfuhrungspfad angeordnet ist.
EN: The system of claim 2, wherein the security monitor is positioned in a core processing pipeline before execution.

### Claim 12
DE: System nach Anspruch 2, wobei baseline arming erst nach Erreichen einer Mindestanzahl von Endpunktproben erfolgt.
EN: The system of claim 2, wherein baseline arming occurs only after reaching a minimum endpoint sample count.

### Claim 13
DE: System nach Anspruch 2, wobei unmatched-route-Anfragen bei aktivierter Baseline eine erhohte Schwere erhalten.
EN: The system of claim 2, wherein unmatched-route requests receive elevated severity after baseline arming.

### Claim 14
DE: System nach Anspruch 2, wobei block den nachgelagerten Laufzeitpfad hart unterbindet.
EN: The system of claim 2, wherein block hard-stops downstream runtime execution.

### Claim 15
DE: Verfahren nach Anspruch 1, wobei Nanodezibelwerte aus einer anaglyphen Forminterferenzmetrik abgeleitet werden.
EN: The method of claim 1, wherein nanodecibel values are derived from an anaglyphic form-interference metric.

### Claim 16
DE: Verfahren nach Anspruch 15, wobei eine Noise-Trace-Memory-Imprint-Komponente (Stigma) zur Verhaltensnachverfolgung gespeichert wird.
EN: The method of claim 15, wherein a noise-trace memory imprint component (stigma) is stored for behavioral traceability.

### Claim 17
DE: Verfahren nach Anspruch 1, wobei high_risk aus dem Vergleich von ndb_score und ndb_threshold bestimmt wird.
EN: The method of claim 1, wherein high_risk is determined by comparing ndb_score and ndb_threshold.

### Claim 18
DE: Verfahren nach Anspruch 1, wobei bei low tide und ndb_score unter Schwellwert submit-Operationen zugelassen werden.
EN: The method of claim 1, wherein submit operations are admitted under low tide and ndb_score below threshold.

### Claim 19
DE: System nach Anspruch 2, wobei active_peers, avg_latency_ms, bandwidth_kbps und load als Telemetrieparameter in die Betriebsklassifikation einfliessen.
EN: The system of claim 2, wherein active_peers, avg_latency_ms, bandwidth_kbps, and load are telemetry parameters used in operating-state classification.

### Claim 20
DE: Computerprogrammprodukt nach Anspruch 3, wobei ein auditierbarer Ereignispfad mit Zeitstempeln fur jede Policy-Entscheidung persistiert wird.
EN: The computer program product of claim 3, wherein an auditable timestamped event path is persisted for each policy decision.
