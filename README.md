Das ist mein IBIS Tester
Damit kann man Fahrzielanzeigen bzw. Innenanzeigen testen, aktuell eingebaut sind:
DS001 (Linie), DS001a (Sonderzeichen), DS003 (Zielnummer), DS021 (Für Anzeigenadresse 1 und 2), DS003a (Zieltext), DS009 (Innenanzeige) und DS003c (Innenanzeige).
Da ich nicht alle testen kann, weil die entsprechenden Geräte vorhanden sind, könnt ihr das gerne ausprobieren

---------------------------------------------------------------------------------------------------------------------------------------------------

Installation (Linux, andere Systeme sind auch möglich):
1. System-Pakete aktualisieren & installieren
Zuerst bringen wir den Pi auf den neuesten Stand und installieren die notwendigen System-Bibliotheken für Python und die grafische Oberfläche.

Öffne ein Terminal und gib ein:

sudo apt update
sudo apt install python3 python3-pip python3-tk -y

---------------------------------------------------------------------------------------------------------------------------------------------------

2. Python-Bibliotheken installieren
Wir benötigen das Modul pyserial, um mit dem USB-zu-RS485/IBIS-Adapter zu sprechen.

pip3 install pyserial

---------------------------------------------------------------------------------------------------------------------------------------------------

3. Ordnerstruktur anlegen
Das Skript erwartet bestimmte Textdateien für die Ziele und Innenanzeigen. Erstelle diese im selben Ordner, in dem auch deine main.py liegt:

Erstelle einen Ordner namens Ziel und darin eine Datei Ziele.txt.

Erstelle einen Ordner namens Innen und darin eine Datei Innen.txt.

Beispielstruktur:

/home/pi/ibis_project/

/home/pi/ibis_project/main.py

/home/pi/ibis_project/Ziel/Ziele.txt

/home/pi/ibis_project/Innen/Innen.txt

Tipp: In den .txt Dateien sollte pro Zeile einfach ein Ziel stehen (z. B. "Hauptbahnhof").

---------------------------------------------------------------------------------------------------------------------------------------------------

4. Berechtigungen für den USB-Port (Optional)
Damit das Skript ohne sudo auf den USB-Adapter (/dev/ttyUSB0) zugreifen kann, musst du deinen Benutzer zur Gruppe dialout hinzufügen:

sudo usermod -a -G dialout $USER

Wichtig: Danach einmal aus- und wieder einloggen oder den Pi neu starten!

---------------------------------------------------------------------------------------------------------------------------------------------------

5. Das Skript starten
Du kannst das Skript nun direkt aus dem Terminal heraus starten:

python3 main.py

---------------------------------------------------------------------------------------------------------------------------------------------------

Profi-Tipp: Automatischer Start beim Booten
Da das Tool im Vollbildmodus läuft, möchtest du wahrscheinlich, dass es direkt nach dem Start des Pi/SBC erscheint.

Erstelle eine Autostart-Datei:

mkdir -p ~/.config/autostart
nano ~/.config/autostart/ibis.desktop

Füge diesen Inhalt ein (Pfade ggf. anpassen):

[Desktop Entry]
Type=Application
Name=IBIS Control
Exec=python3 /home/pi/ibis_project/main.py

Speichern mit Strg+O, Enter und Beenden mit Strg+X.

--------------------------------------------------------------------------------------------------------------------------------------------------

//WICHTIG:
Es kann sein dass das Programm sich weigert den Port zu öffnen/nutzen, dazu einfach das programm mit sudo starten.
Auch kann es sein dass der "Sofort Neustart" ein Passwort benötigt (wegen sudo reboot)
Für beides gibt es die möglichkeit die Passworteingabe zu "überspringen":

sudo visudo

pi ALL=(ALL) NOPASSWD: /usr/bin/python3 
#Ermöglicht Autostart ohne Passworteingabe

pi ALL=(ALL) NOPASSWD: /sbin/reboot 
#Ermöglicht den Sofort Neustart ohne Passworteingabe

---------------------------------------------------------------------------------------------------------------------------------------------------

Support:
Bei Fragen oder Datensatzvorschlägen (mit Beispielen) gerne ein Issue öffnen
