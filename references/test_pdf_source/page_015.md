erfolgreich Probleme wie Korrelationen zwischen aufeinanderfolgenden Trainingsbeispielen und nicht stationäre Verteilungen der Eingaben.

Somit bildet die Arbeit von Lin (1992) einen entscheidenden historischen Meilenstein und die theoretische Basis für die modernen Ansätze im Deep Reinforcement Learning, die Experience Replay als Standardkomponente verwenden.

Darum soll auch in dieser Abschlussarbeit untersucht werden, wie effektiv Experience Replay gegenüber RBQL ist.

## 3.3 Recursive Backwards Q-Learning

Das Paper Recursive Backwards Q-Learning in Deterministic Environments beschreibt die Idee des RBQL. In diesem Paper wird bemängelt, dass Q-Learning Agenten häufig verfügbare Informationen ignorieren und es mehrere Episoden dauert, bis ein Fehler zum Ausgangszustand zurück propagiert ist, selbst wenn der Agent dem „optimalen Pfad" folgt. Es schlägt als Verbesserung den RBQL Agenten vor, welcher nach Erreichen eines Endzustandes rekursiv die bereits erkundeten Zustände bewertet. Das Paper gibt als Lernfunktion Gleichung 3.1 an. Dadurch hänge der Q-Wert nur noch von der Belohnung und dem besten Nachbarn ab. [4]

$$Q(S_t, A_t) = R_{t+1} + \gamma \max_a Q(S_{t+1}, a) \tag{3.1}$$

Angewandt wird der RBQL-Agent in dieser Arbeit an einer zweidimensionalen Gitterwelt. Diese Gitterwelt ist ein Labyrinth, aus dem der Agent herausfinden soll. Für jede Richtung, in die sich der Agent bewegen kann, gibt es eine Aktion. Dies macht vier mögliche Aktionen, zwischen denen der Agent wählen kann. Wenn der Agent durch eine Aktion eine Wand berühren würde, wird die Aktion nicht ausgeführt. Es gibt drei unterschiedliche Belohnungen, die dem Agenten helfen sollen, zu lernen. Negative Belohnungen gibt es für jede normale Kachel und für das Berühren einer Wand. Dabei ist die Belohnung für das Berühren einer Wand niedriger als die für eine normale Kachel, damit der Agent lernt, keine Wände zu berühren. Die negative Belohnung für eine normale Kachel existiert, „um den Agenten von unnötigen Schritten abzuhalten". [4] Wenn der Agent den Endzustand erreicht, erhält er eine Belohnung von 10.

Das Besondere im Vergleich zu einem klassischen Q-Learning Agenten ist, dass beim RBQL jeder Schritt, der erkundet wird, auch gespeichert wird. Hier geschieht dies in einem zweidimensionalen Array. Als Indizes werden der vorherige Zustand und die ausgewählte Aktion genommen. An dieser Stelle wird dann der durch die Aktion erreichte Folgezustand gespeichert. Außerdem gibt es noch ein zweites zweidimensionales Array, welches die gleichen Indizes verwendet, aber die jeweiligen zugehörigen Belohnungen speichert. Um
