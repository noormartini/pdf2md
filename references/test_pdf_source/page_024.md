1 def rbql_update(final_state):
2
global Q, gamma, reverse_steps, rewards
3
visited = set()
4
queue = [final_state]
5
6
while len(queue) > 0:
7
current_state = queue.pop()
8
if current_state in visited:
9
continue
10
visited.add(current_state)
11
for step in reverse_steps.get(current_state, []):
12
if step[2] == current_state:
13
Q[step[0]][step[1]] = rewards[step[0]][step[1]] + gamma * np.max
(Q[step[2]])
14
queue.insert(0, step[0])
Quellcode 5.5: Methode rbql_update
5.4 Vergrößerung des Zustandraums
Um den Agenten das Lernen zu erschweren und so die Unterschiede zwischen den Agenten
besser hervorzuheben, wird der Zustandsraum vergrößert. Dies wird durch eine Vergrö-
ßerung des Spielfeldes umgesetzt. So hat sich der Zustandsraum von 7.488 Zuständen auf
59.904 Zustände erweitert, was die Komplexität des Lernprozesses deutlich erhöht. Quell-
code 5.6 Dies macht einen erheblichen Unterschied, da die Q-Funktion nun für deutlich
mehr Zustände approximiert werden muss.
Quellcode 5.7 zeigt die angepasste Methode getState, welche die fünf Vektoren x_ball,
y_ball, vx_ball, vy_ball und x_racket auf eine eindeutige Zahl abbildet.
Weiterhin muss noch die Logik angepasst werden, wann der Ball auf eine Wand trifft.
1
num_of_states = 26*24*2*2*24
Quellcode 5.6: Berechnung der Anzahl der States bei Verdopplung der Größe des Spielfeldes
1 def getState(x_ball, y_ball, vx_ball, vy_ball, x_racket):
2
return ((((x_ball * 26 + y_ball) * 2 + (vx_ball + 1)//2) * 2 + (vy_ball +
1)//2) * 24 + x_racket)
Quellcode 5.7: Methode getState nach Verdopplung der Spielfeldgröße
5.5 Mögliche Optimierung des RBQL
Beim RBQL werden beim Erreichen eines Endzustands standardmäßig alle Zustände, die
zu dem aktuellen Endzustand führen, bewertet. Dabei wird nicht beachtet, ob ein Zustand
18