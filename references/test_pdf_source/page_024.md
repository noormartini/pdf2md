```python
def rbql_update(final_state):
    global Q, gamma, reverse_steps, rewards
    visited = set()
    queue = [final_state]

    while len(queue) > 0:
        current_state = queue.pop()
        if current_state in visited:
            continue
        visited.add(current_state)
        for step in reverse_steps.get(current_state, []):
            if step[2] == current_state:
                Q[step[0]][step[1]] = rewards[step[0]][step[1]] + gamma * np.max(Q[step[2]])
                queue.insert(0, step[0])
```

**Quellcode 5.5**: Methode rbql_update

## 5.4 Vergrößerung des Zustandraums

Um den Agenten das Lernen zu erschweren und so die Unterschiede zwischen den Agenten besser hervorzuheben, wird der Zustandsraum vergrößert. Dies wird durch eine Vergrößerung des Spielfeldes umgesetzt. So hat sich der Zustandsraum von 7.488 Zuständen auf 59.904 Zustände erweitert, was die Komplexität des Lernprozesses deutlich erhöht. Quellcode 5.6 zeigt dies. Es macht einen erheblichen Unterschied, da die Q-Funktion nun für deutlich mehr Zustände approximiert werden muss.

Quellcode 5.7 zeigt die angepasste Methode getState, welche die fünf Vektoren x_ball, y_ball, vx_ball, vy_ball und x_racket auf eine eindeutige Zahl abbildet.

Weiterhin muss noch die Logik angepasst werden, wann der Ball auf eine Wand trifft.

```python
num_of_states = 26*24*2*2*24
```

**Quellcode 5.6**: Berechnung der Anzahl der States bei Verdopplung der Größe des Spielfeldes

```python
def getState(x_ball, y_ball, vx_ball, vy_ball, x_racket):
    return ((((x_ball * 26 + y_ball) * 2 + (vx_ball + 1)//2) * 2 + (vy_ball + 1)//2) * 24 + x_racket)
```

**Quellcode 5.7**: Methode getState nach Verdopplung der Spielfeldgröße

## 5.5 Mögliche Optimierung des RBQL

Beim RBQL werden beim Erreichen eines Endzustands standardmäßig alle Zustände, die zu dem aktuellen Endzustand führen, bewertet. Dabei wird nicht beachtet, ob ein Zustand
