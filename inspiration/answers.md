# Antworten zu den Theorie- und Verständnisfragen

## TCP-Rechen-Server: Pakete und Python-Code

| Paket | Auslöser im Code | Wirkung |
|---|---|---|
| SYN | `sock.connect()` im Client | Client möchte Verbindung aufbauen |
| SYN+ACK | `sock.accept()` im Server (Kernel) | Server bestätigt, `accept()` kehrt erst nach dem ACK zurück |
| ACK | `sock.connect()` im Client (Kernel) | Handshake abgeschlossen, `connect()` kehrt zurück |
| PSH/ACK mit Request | `sock.sendall()` im Client | Daten (Header + Zahlen) werden übertragen |
| ACK | Server-Kernel, während `recv()` blockiert | bestätigt Empfang, `recv()` liefert die Bytes |
| PSH/ACK mit Response | `conn.sendall()` im Server | Antwort wird übertragen |
| ACK | Client-Kernel, während `recv()` blockiert | bestätigt Empfang, `recv()` liefert die Antwort |
| FIN/ACK | `sock.close()` bzw. Timeout-Schließen | Verbindungsabbau |

Blockierende Befehle werden also durch die Ankunft des jeweiligen
Gegenpakets abgeschlossen:

- `connect()` → SYN+ACK (und eigener ACK)
- `accept()` → ACK des Clients nach dem Handshake
- `recv()` → PSH/ACK mit Nutzdaten; bei Timeout gar kein Paket

Bei großen Anfragen (mehr als ein Segment) liefert ein einzelner `recv()` nur
einen Teil. Deshalb liest der Server zuerst exakt 9 Bytes Header und dann
exakt 4·N Bytes. `sendall()` zerlegt die Nachricht bei Bedarf selbst in
mehrere Segmente.

## Lokale IP-Adresse und Port im Client

1. **Herausfinden:** `sock.getsockname()` liefert `(IP, Port)` des lokalen
   Sockets; `sock.getpeername()` liefert die Gegenseite. Nach `connect()`
   sind beide gesetzt.
2. **Wann und woher:** Erst beim `connect()` vergibt das Betriebssystem einen
   freien ephemeren Quellport und wählt die Quell-IP anhand der Route zum
   Ziel. Vorher ist der lokale Port bei einem nicht gebundenen Socket 0.
3. **Selbst festlegen:**

   ```python
   sock.bind(("192.168.1.10", 51000))
   sock.connect((server_ip, server_port))
   ```

   Mit Port `0` wählt das Betriebssystem weiterhin selbst einen freien Port.

## Timeouts und `try … except`

Ohne Timeout blockiert `recv()` unbegrenzt, wenn der Peer nicht antwortet.
Das Programm „hängt“ dann. `settimeout(10)` lässt blockierende Socket-Aufrufe
nach 10 Sekunden `socket.timeout` (Unterklasse von `OSError`) auslösen.
`try … except socket.timeout:` fängt genau diesen Fehler ab und erlaubt eine
kontrollierte Reaktion (Verbindung schließen, weitermachen, Meldung).

Ein gemeinsamer Timeout für alle Sockets:

```python
socket.setdefaulttimeout(10)
```

## TCP und UDP auf demselben Port

Ja, das funktioniert. TCP und UDP sind getrennte Protokolle mit eigenen
Port-Tabellen; ein TCP-Socket auf Port 50000 und ein UDP-Socket auf Port 50000
kollidieren nicht. `calc/server_both_protocols.py` zeigt das: Der TCP-Server
läuft in einem Thread, der UDP-Server im Hauptthread, beide binden denselben
Port. Ein Client kann wahlweise per TCP oder UDP denselben Port ansprechen.

## Pipelining

TCP ist ein Byte-Strom ohne Nachrichtengrenzen. Ein `recv()` kann daher das
Ende einer Anfrage und den Anfang der nächsten enthalten. `RequestStream`
puffert alle gelesenen Bytes und schneidet anhand von `N` genau eine Anfrage
heraus. Der Rest bleibt im Puffer für den nächsten Aufruf. So kann der Server
mehrere direkt hintereinander gesendete Anfragen korrekt trennen und in
Empfangsreihenfolge beantworten. Der Client ordnet die Antworten über die ID
zu.

## Mail

`MAIL FROM`/`RCPT TO` bilden den SMTP-Umschlag (Zustellung), `From:`/`To:` im
Header nur den Briefkopf. Beide sind unabhängig, weshalb sich der angezeigte
Absender fälschen lässt. Die Mailserver ergänzen beim Transport u. a.
`Received`, `Return-Path`, `Authentication-Results`, `DKIM-Signature` und
`ARC`-Header. Umlaute im Betreff müssen als `=?utf-8?B?<Base64>?=` kodiert
werden; der Body wird über `Content-Type: text/plain; charset=utf-8` und
`Content-Transfer-Encoding: 8bit` korrekt dargestellt.
