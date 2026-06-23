# Kapitel 5
**Implementierung**
Die Q-Learning Agenten werden in der Programmiersprache Python implementiert. Als
Vorlage für das Ping-Pong Spiel wird das Beispiel aus Maschinelles Lernen für Dum-
mies®: Maschinelles Lernen richtig verstehen : GPT-Sprachmodell, Deep Learning, neu-
ronales Q-Learning - alles selbst programmieren : viele Code-Beispiele zu allen behan-
delten Themen genommen. [8, S. 283–285] Der in diesem Buch bereits umgesetzte Expe-
rience Replay Q-Learning Agent wird später auch benutzt, um die Lernergebnisse mit den
anderen Algorithmen zu vergleichen.
Der Zustand der Umgebung setzt sich in diesem Beispiel aus der x- und y-Koordinate
des Balles, der Geschwindigkeit des Balles in x- und y-Richtung, und der Position des
Schlägers in x-Richtung zusammen.
1 def getState(x_ball, y_ball, vx_ball, vy_ball, x_racket):
2
return (((x_ball*13 +y_ball)*2 +(vx_ball+1)/2)*2 +(vy_ball+1)/2)*12 +
x_racket
Quellcode 5.1: Methode getState [8, S. 284]
In Quellcode 5.1 ist dargestellt, wie aus den 5 Koordinaten „x_ball“, „y_ball“, „vx_ball“,
„vy_ball“ und „x_racket“ eine Zahl berechnet wird, die den Zustand eindeutig beschreibt.
Wichtig ist hierbei die Eindeutigkeit der Abbildung, damit zwei Zustände nicht auf den-
selben Wert abgebildet werden.
1 def getAction(state): # gibt -1 für Schläger links oder +1 für rechts zurück
2
global epsilon, Q
3
if np.random.rand() <= epsilon:
4
return np.random.choice([-1, 1])
5
return (np.argmax(Q[int(state)]) * 2) - 1
Quellcode 5.2: Methode getAction [8, S. 283]
Quellcode 5.2 zeigt die Funktion, welche genutzt wird, um eine Aktion auszuwählen. Da-
bei wird mit einer Wahrscheinlichkeit Epsilon eine zufällige Aktion ausgewählt. Dadurch
werden auch Aktionen mit einem niedrigeren Q-Wert ausprobiert, um eventuell bessere
Aktionen zu finden. Epsilon wird jede Runde schrittweise um einen festen Betrag redu-
ziert, bis Epsilon null erreicht. Wenn keine zufällige Aktion ausgewählt wird, wird die
15