# Socketprogrammierung WS26 – Lösungen

Alle Übungen aus `AIN RN - Laboraufgabe - Socketprogrammierung WS26.docx`
als lauffähige Python-Skripte.

## Struktur

```
inspiration/
├── calc/
│   ├── protocol.py                 # gemeinsames Nachrichtenformat (struct)
│   ├── server_tcp_serial.py        # TCP-Server, seriell
│   ├── client_tcp_serial.py        # TCP-Client, seriell
│   ├── server_udp.py               # UDP-Server
│   ├── client_udp.py               # UDP-Client
│   ├── server_tcp_threaded.py      # Threads + Pipelining
│   ├── client_tcp_pipeline.py      # Client mit einem sendall()
│   └── server_both_protocols.py    # TCP und UDP auf demselben Port
├── mail/
│   ├── openssl_smtp.md             # SMTP per OpenSSL
│   └── smtp_client.py              # SMTP-Client mit Sockets
├── answers.md                      # Theorie- und Verständnisfragen
└── README.md
```

## Nachrichtenformat

Anfrage: `<ID:!I><Operation:3s><N:!H><z1..zN:!i>` → 9 Bytes + 4·N Bytes
Antwort: `<ID:!I><Ergebnis:!i>` → 8 Bytes

`protocol.py` kapselt `pack`/`unpack`, die Berechnung und gepufferte Lese-
Funktionen. Durch den Puffer gehen bei mehreren `recv()`-Aufrufen keine Bytes
verloren; dadurch funktioniert auch Pipelining mit Nachrichtengrenzen.

## Lokal starten

Zwei Terminals, jeweils im Ordner `inspiration/calc`:

```bash
python3 server_tcp_serial.py
python3 client_tcp_serial.py
```

UDP:

```bash
python3 server_udp.py
python3 client_udp.py
```

Threads + Pipelining:

```bash
python3 server_tcp_threaded.py
python3 client_tcp_pipeline.py
```

Der Client `client_tcp_serial.py` stellt fünf Aufgaben, darunter eine mit
20.000 Zahlen (ca. 80 KB). Damit wird die Anfrage auf mehrere TCP-Segmente
verteilt. Der Server liest zuerst die 9 Header-Bytes und danach genau 4·N Bytes.

## Im Netzwerk testen

Auf dem Server-Rechner:

```bash
python3 server_tcp_threaded.py --host 0.0.0.0 --port 50000
```

Auf dem Client-Rechner (IP des Servers einsetzen):

```bash
python3 client_tcp_pipeline.py --host 100.x.y.z --port 50000
```

Die eigene IP ermittelt man mit `ip addr`/`ifconfig` (Linux/macOS) bzw.
`ipconfig` (Windows). Firewall muss eingehende Verbindungen auf dem Port
erlauben.

## 10-Sekunden-Timeout testen

```bash
telnet 127.0.0.1 50000
```

Nichts eingeben: Nach 10 Sekunden schließt der Server die Verbindung
(`socket.timeout` in `receive`/`handle_connection`). In Wireshark sieht man
danach das FIN des Servers.

## UDP-Grenze

Ein UDP-Datagramm transportiert höchstens 65.507 Bytes Nutzdaten. Mit 9 Bytes
Header und 4 Bytes pro Zahl ergibt sich `N <= 16374`. Größere Anfragen werden
in `client_udp.py` nicht erzeugt.

## Mail

`mail/openssl_smtp.md` beschreibt den interaktiven SMTP-Dialog über OpenSSL.
Der Python-Client sendet eine Mail mit vollständigem Header (inkl. Umlauten):

```bash
cd mail
export SMTP_USER='rz-account'
export MAIL_TO='empfaenger@example.com'
python3 smtp_client.py
```

Das Passwort wird interaktiv abgefragt oder über `SMTP_PASSWORD` gesetzt.
`MAIL_FROM` ist optional und fällt auf `SMTP_USER` zurück.

Der Client benutzt bewusst weder `smtplib` noch `email`; nur
`email.utils.formatdate()` und `email.utils.make_msgid()` sind erlaubt.
