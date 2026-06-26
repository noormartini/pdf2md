Anzahl der Schritte übereinstimmt, die bereits bewertet sind, bleibt die Warteschlange leer und es wird keine neue Bewertung durchgeführt. Wenn der Folgezustand des letzten neuen Schrittes mit dem Endzustand übereinstimmt, werden alle Zustände, die in diesen Endzustand führen, neu bewertet. In allen anderen Fällen wird der Folgezustand des letzten noch nicht bewerteten Schrittes der Warteschlange angefügt. Dadurch werden nur noch Teile des Baumes bewertet, die neu hinzugekommen sind.

```python
def rbql_update(final_state):
    global Q, gamma, reverse_steps, last_step_updated, last_step, cnt_steps_taken
    visited = set()
    queue = []
    #no update without new steps
    if cnt_steps_taken == last_step_updated:
        queue = []
    #update all
    elif (last_step[2] == final_state) or last_step_updated == 0:
        queue.append(final_state)
    #update shortend
    else:
        queue.append(last_step[2])

    while queue:
        current_state = queue.pop()
        if current_state in visited:
            continue
        visited.add(current_state)
        for step in reverse_steps.get(current_state, []):
            if step[2] == current_state:
                Q[step[0]][step[1]] = rewards[step[0]][step[1]] + gamma * np.max(Q[step[2]])
                queue.insert(0, step[0])

    last_step_updated = cnt_steps_taken
```

**Quellcode 5.8**: Optimierte RBQL update Methode

### 5.6 RBQL in einer nicht deterministischen Umgebung

In dem Paper Recursive Backwards Q-Learning in Deterministic Environments wird als mögliche Richtung für weiterführende Forschung vorgeschlagen, zu untersuchen, wie RBQL in einer teils nicht-deterministischen Umgebung lernt. Dies soll hier nun betrachtet werden. Dazu wird in dem Ping-Pong Spiel mit einer kleiner Wahrscheinlichkeit die Geschwindigkeit des Balles in X- und Y-Richtung verändert. Die Geschwindigkeit kann da-
