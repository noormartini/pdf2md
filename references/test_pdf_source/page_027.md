durch in einem Bereich zwischen minus zwei und zwei liegen. In Quellcode 5.9 ist die Geschwindigkeitsanpassung dargestellt. Dazu wird zunächst ein Zufallswert „rand" erzeugt. Wenn dieser Zufallswert kleiner als 0,02 ist, wird die Geschwindigkeit des Balles verändert. Dabei wird zunächst die Geschwindigkeit in X-Richtung verändert, indem zur aktuellen Geschwindigkeit zufällig entweder eins addiert oder subtrahiert wird. Anschließend wird der resultierende Wert auf den Bereich [−2, 2] begrenzt. Danach erfolgt eine Anpassung der Geschwindigkeit in Y-Richtung auf die gleiche Weise. Abschließend muss noch dafür gesorgt werden, dass der Ball bei einer höheren Geschwindigkeit das Spielfeld nicht ungewollt verlässt. Bisher wird das dadurch gelöst, dass wenn eine Koordinate des Balles über den Spielfeldrand hinausgeht, die Geschwindigkeit invertiert wird. Wenn der Ball aber eine Geschwindigkeit von zwei hat und schon genau ein Feld vor dem Spielfeldrand ist, kann es vorkommen, dass der Ball in einer Episode einen Schritt über den Spielfeldrand hinausgeht. Da dies aber kein legaler Zustand ist, wird die maximalen X- und Y-Koordinaten des Balles nun noch fest limitiert. Wenn der Ball den Rand dann erreicht, wird die Geschwindigkeit der jeweiligen Achse trotzdem, wie bisher auch, noch mit minus eins multipliziert, um die Geschwindigkeit zu invertieren.

```python
rand = random.random()

# Geschwindigkeitsanpassung
if rand < 0.02:
    vx_ball += random.choice([-1, 1])
    vx_ball = max(min(vx_ball, 2), -2) # Begrenzung auf [-2, 2]
    vy_ball += random.choice([-1, 1])
    vy_ball = max(min(vy_ball, 2), -2) # Begrenzung auf [-2, 2]

x_ball = max(0, min(x_ball, 12)) # 0-12
y_ball = max(0, min(y_ball, 12)) # 0-11
```

**Quellcode 5.9**: Geschwindigkeitsanpassung für die nicht deterministische Umgebung

Die Geschwindigkeit des Balles kann nun in jede Richtung vier unterschiedliche Werte annehmen. Durch diese Anpassung hat sich der Zustandsraum leicht erhöht. Damit die getState Funktion trotzdem noch für jeden Zustand einen eindeutigen Wert zurückgibt, muss diese entsprechend angepasst werden. Diese Anpassung ist in Quellcode 5.10 zu sehen. Um die vier Werte [−2, −1, 1, 2], die von der Geschwindigkeit angenommen werden können, nur durch positive Werte darzustellen, wird ein Dictionary verwendet, welches jedem Wert einen positiven Wert zuordnet. So ist die Geschwindigkeit für die Berechnung des Zustandes im Bereich von null bis drei. In den bisherigen Versionen kann die Geschwindigkeit nur die Werte minus eins und eins annehmen. Um diese Werte auf positive Zahlen abzubilden, wird zu der Geschwindigkeit eins addiert und durch zwei geteilt. So bekommt man für die Geschwindigkeit minus eins das Ergebnis null und für die Ge-
