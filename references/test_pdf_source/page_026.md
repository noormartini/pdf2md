Anzahl der Schritte übereinstimmt, die bereits bewertet sind, bleibt die Warteschlange leer
und es wird keine neue Bewertung durchgeführt. Wenn der Folgezustand des letzten neuen
Schrittes mit dem Endzustand übereinstimmt, werden alle Zustände, die in diesen Endzu-
stand führen, neu bewertet. In allen anderen Fällen wird der Folgezustand des letzten noch
nicht bewerteten Schrittes der Warteschlange angefügt. Dadurch werden nur noch Teile
des Baumes bewertet, die neu hinzugekommen sind.
1 def rbql_update(final_state):
2
global Q, gamma, reverse_steps, last_step_updated, last_step,
cnt_steps_taken
3
visited = set()
4
queue = []
5
#no update without new steps
6
if cnt_steps_taken == last_step_updated:
7
queue = []
8
#update all
9
elif (last_step[2] == final_state) or last_step_updated == 0:
10
queue.append(final_state)
11
#update shortend
12
else:
13
queue.append(last_step[2])
14
15
while queue:
16
current_state = queue.pop()
17
if current_state in visited:
18
continue
19
visited.add(current_state)
20
for step in reverse_steps.get(current_state, []):
21
if step[2] == current_state:
22
Q[step[0]][step[1]] = rewards[step[0]][step[1]] + gamma * np.max
(Q[step[2]])
23
queue.insert(0, step[0])
24
25
last_step_updated = cnt_steps_taken
Quellcode 5.8: Optimierte RBQL update Methode
5.6 RBQL in einer nicht deterministischen Umgebung
In dem Paper Recursive Backwards Q-Learning in Deterministic Environments wird als
mögliche Richtung für weiterführende Forschung vorgeschlagen, zu untersuchen, wie RB-
QL in einer teils nicht-deterministischen Umgebung lernt. Dies soll hier nun betrachtet
werden. Dazu wird in dem Ping-Pong Spiel mit einer kleiner Wahrscheinlichkeit die Ge-
schwindigkeit des Balles in X- und Y-Richtung verändert. Die Geschwindigkeit kann da-
20