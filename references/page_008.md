könnten solche Sprachmodelle mit RBQL trainiert werden, wodurch das Training optimiert werden könnte.

### 1.2 Zielsetzung der Arbeit

Diese Arbeit, welche im Rahmen einer Abschlussarbeit des Bachelorstudiengangs Informatik an der Technischen Hochschule Mannheim entstanden ist, beschäftigt sich damit, ob in deterministischen Umgebungen mit dem RBQL neuronale Netzwerke effizient trainiert werden können.

Dies wird am Anwendungsfall eines Ping-Pong-Spiels getestet. Dabei soll ein neuronales Netz lernen, den Ball mit einem Schläger in der Luft zu halten, ohne dass der Ball herunterfällt. Das neuronale Netz wird hierbei durch das RBQL trainiert.

Die Algorithmen RBQL, Experience Replay Q-Learning und das klassische Q-Learning werden zunächst ohne neuronale Netze zum Trainieren des Ping-Pong-Agenten eingesetzt und die Ergebnisse analysiert. Anschließend soll noch gezeigt werden, wie effizient ein einfaches neuronales Netz mit dem RBQL trainiert werden kann und das Ergebnis mit dem verbreiteten Experience Replay Q-Learning verglichen werden. Daraus sollen dann Schlüsse gezogen werden, ob RBQL das Training neuronaler Netze verbessern kann.

> Kann das Training von neuronalen Netzen in deterministischen Umgebungen durch RBQL effizienter gestaltet werden als mit dem bisher verbreiteten Experience Replay Q-Learning?
