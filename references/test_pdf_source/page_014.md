komplexeren Umgebung als bis dahin üblich, und zweitens die Entwicklung von Verfahren
zur Beschleunigung des Lernprozesses.
Als eine dieser Beschleunigungsmaßnahmen schlug Lin Experience Replay vor, ein Kon-
zept, bei dem der Agent Übergänge der Form (st, at, rt, st+1) speichert und später mehr-
fach für Updates seiner Wertfunktionen verwendet. Dieses Vorgehen adressiert zwei Schwä-
chen klassischer Reinforcement Learning Algorithmen: Zum einen gehen seltene, aber
für den Lernprozess besonders wichtige Erfahrungen in klassischen Online-Verfahren oft
schnell wieder „verloren“, weil sie nur einmal verarbeitet werden. Zum anderen erlaubt
Experience Replay eine effizientere Nutzung von Trainingsdaten, was insbesondere dann
hilfreich ist, wenn das Sammeln neuer Erfahrungen teuer oder gefährlich ist. Lin formuliert
diese Idee explizit und schlägt vor, die gespeicherten Übergänge nicht einfach in chronolo-
gischer Reihenfolge wiederzugeben, sondern durch sogenanntes Backward Replay gezielt
von Endzuständen zurückzugehen, um die Kreditzuweisung (credit assignment) über lan-
ge Zeithorizonte hinweg zu beschleunigen.
In seinen Experimenten vergleicht Lin acht verschiedene Frameworks, darunter Varian-
ten von Q-Learning und AHC mit und ohne Experience Replay, sowie weitere Techniken
wie die Nutzung von Aktionsmodellen für Planung und „Teaching“, d.h. Lernen durch das
Nachspielen von Beispielen eines Experten. Getestet werden diese Ansätze in einer simu-
lierten, dynamischen Umgebung, in der ein Agent überleben musste, indem er Nahrung
sucht und gleichzeitig feindlichen Objekten ausweicht. Die Umgebung ist nicht trivial:
Sie ist stochastisch, teilweise beobachtbar und erforderte vom Agenten die Koordination
mehrerer Ziele unter Unsicherheit.
Die Ergebnisse zeigen deutlich, dass Experience Replay die Lernrate erheblich steigern
konnte, insbesondere in den frühen Lernphasen. Lin weist zudem darauf hin, dass Ex-
perience Replay nur dann effektiv ist, wenn die zugrunde liegenden Umweltgesetze über
die Zeit konstant bleiben, da ansonsten gespeicherte Erfahrungen an Aussagekraft verlie-
ren oder sogar schädlich sein könnten. Eine weitere wichtige Erkenntnis ist, dass bei sto-
chastischen Entscheidungsstrategien nicht jede gespeicherte Erfahrung in gleichem Maße
wiederverwendet werden sollte: Erfahrungen, die unter der aktuellen Strategie nur mit sehr
geringer Wahrscheinlichkeit auftreten würden, können den Lernprozess sogar negativ be-
einflussen. [14]
Diese Arbeit von Lin gilt als die erste systematische Darstellung des Experience Replay
und wird daher als Ursprung dieses Konzepts angesehen. Sie hat die theoretische Grundla-
ge für spätere Arbeiten gelegt, insbesondere für den Deep Q-Network (DQN) Algorithmus
von Mnih u. a. [15], der Experience Replay als zentrale Technik nutzt, um neuronale Net-
ze für Q-Learning effizient und stabil zu trainieren. Mnih u. a. kombinieren die von Lin
eingeführte Idee des Replay-Buffers mit tiefen neuronalen Netzen und adressieren damit
8