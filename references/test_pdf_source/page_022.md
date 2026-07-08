Aktion mit dem höchsten Q-Wert ausgewählt. Die Aktion mit dem höchsten Q-Wert verspricht die größte Belohnung.

Jeder der untersuchten Q-Learning Agenten besitzt eine eigene Update-Funktion zur Aktualisierung der Q-Werte.

## 5.1 Experience Replay

Der Quellcode für das Experience Replay stammt aus dem oben genannten Buch [8, S. 283–285]. Quellcode 5.3 zeigt die Funktion zum Aktualisieren der Q-Werte unter Zuhilfenahme von Experience Replay. Dabei werden zuerst die Replay-Buffer befüllt und anschließend die Q-Werte von X zufälligen Zuständen aus dem Replay Buffer aktualisiert. X ist dabei die sogenannte Batch Size. Das Betrachten bereits gemachter Erfahrungen reduziert die Anzahl der Episoden, bis der Agent das Spiel gelernt hat.

```python
def updateQ(reward, state, action, nextState):
    global er_re, er_s, er_a, er_ns, tick, Q, alpha, gamma
    # Replay-Buffer füllen
    er_re[tick%400] = reward   # experience replay Belohnung
    er_s[tick%400] = state     # experience replay Zustand
    er_a[tick%400] = action    # experience replay Aktion
    er_ns[tick%400] = nextState# experience replay nächster Zustand

    for i in range(batch_size):
        r = random.randint(0, 399)
        # Q[s][a]+=r+alpha*(gamma * max_a' Q(s',a')-Q(s,a))
        Q[int(er_s[r])][int(er_a[r])] += er_re[r] + alpha*(gamma * np.max(Q[int(er_ns[r])]) - Q[int(er_s[r])][int(er_a[r])])
```

**Quellcode 5.3**: Methode updateQ bei Q-Learning mit Experience Replay [8, S. 283]

## 5.2 Q-Learning

Beim Q-Learning wird die Q-Funktion, wie in Gleichung (2.2) zu sehen, nach jeder Episode aktualisiert. Dies ist in Quellcode 5.4 in Python umgesetzt. Dabei wird die Erfahrung, die über die Runde gemacht wird, allerdings nicht betrachtet und nur der letzte Q-Wert aktualisiert. Dadurch benötigt Q-Learning ohne Experience Replay deutlich länger, um eine optimierte Q-Funktion zu approximieren.

```python
def updateQ(reward, state, action, nextState):
    Q[int(state)][int(action)] += alpha * (reward + gamma * np.max(Q[int(nextState)]) - Q[int(state)][int(action)])
```

**Quellcode 5.4**: Methode updateQ bei Q-Learning ohne Experience Replay
