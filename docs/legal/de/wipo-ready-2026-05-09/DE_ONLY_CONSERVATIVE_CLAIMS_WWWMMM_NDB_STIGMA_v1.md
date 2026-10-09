# DE-Only Conservative Claims (Working v1)

Dokumenttyp: Anspruchssatz (konservativ) fur DPMA-Abstimmung
Fokus: Klare technische Wirkung, reduzierte spekulative Formulierung
Datum: 2026-05-09

## Rechtlicher Hinweis
Dieses Dokument ist technische Vorarbeit und keine Rechtsberatung. Endfassung nur durch zugelassenen Patentanwalt.

## Unabhangige Anspruche

### Anspruch 1 (Verfahren)
Computerimplementiertes Verfahren zur Sicherheitsklassifikation von API-Anfragen, umfassend:
1. Empfangen einer Anfrage mit Endpunktkennung;
2. Ermitteln eines Resonanzwertes in Nanodezibel;
3. Speichern endpunktspezifischer Historienwerte;
4. Berechnen einer Baseline nach Erreichen einer Mindestanzahl von Historienwerten;
5. Bestimmen einer Abweichung zwischen Resonanzwert und Baseline;
6. Zuordnen eines Schweregrades anhand mindestens zweier Schwellwerte; und
7. Auswahlen einer Laufzeitrichtlinie aus allow, monitor, throttle oder block.

### Anspruch 2 (System)
System mit API-Laufzeitdienst, Sicherheitsmonitor, Lernkomponente und Richtlinien-Gate, eingerichtet zur Durchfuhrung des Verfahrens nach Anspruch 1.

### Anspruch 3 (Computerprogrammprodukt)
Nichtfluchtiges computerlesbares Medium mit Instruktionen, die bei Ausfuhrung das Verfahren nach Anspruch 1 bewirken.

## Abhangige Anspruche

### Anspruch 4
Verfahren nach Anspruch 1, wobei die Baseline Mittelwert, Median und Standardabweichung in einem gleitenden Fenster umfasst.

### Anspruch 5
Verfahren nach Anspruch 1, wobei die Schweregradzuordnung einen Route-Match-Indikator berucksichtigt.

### Anspruch 6
Verfahren nach Anspruch 1, wobei throttle eine konfigurierbare Verkehrsreduktionskomponente umfasst.

### Anspruch 7
Verfahren nach Anspruch 1, wobei ein negativer ndb_delta-Wert fur eine Risikodeeskalation genutzt wird.

### Anspruch 8
Verfahren nach Anspruch 1, wobei ein Tide-Zustand als zusatzliches Steuerungssignal fur Richtlinienumschaltung verwendet wird.

### Anspruch 9
Verfahren nach Anspruch 1, wobei ein stigma_level die Freigabe von Endpunktaktionen beeinflusst.

### Anspruch 10
Verfahren nach Anspruch 1, wobei Ereignisse strukturierte Felder endpoint, action, stigma_level, ndb_score und outcome enthalten.

### Anspruch 11
System nach Anspruch 2, wobei der Sicherheitsmonitor in einer Kernverarbeitungspipeline vor dem Ausfuhrungspfad angeordnet ist.

### Anspruch 12
System nach Anspruch 2, wobei baseline arming erst nach Erreichen einer Mindestanzahl von Endpunktproben erfolgt.

### Anspruch 13
System nach Anspruch 2, wobei unmatched-route-Anfragen bei aktivierter Baseline mit erhohter Schwere bewertet werden.

### Anspruch 14
System nach Anspruch 2, wobei block den nachgelagerten Laufzeitpfad unterbindet.

### Anspruch 15
Verfahren nach Anspruch 1, wobei active_peers, avg_latency_ms, bandwidth_kbps und load zur Betriebsklassifikation herangezogen werden.

## Abstimmungsnotizen fur Patentanwalt
1. Terminologie in der Endfassung vereinheitlichen (Nanodezibel/ndB).
2. Produktnamen in den Anspruchen vermeiden, nur technische Merkmale verwenden.
3. Trade-Secret-Bestandteile (Parameter-Tuning) in der Beschreibung begrenzen.
