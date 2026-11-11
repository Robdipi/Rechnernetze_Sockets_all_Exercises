# Mail per OpenSSL (SMTP)

## Verbindung öffnen

```
openssl s_client -starttls smtp -crlf -connect asmtp.htwg-konstanz.de:587
```

Nach dem TLS-Handshake meldet sich der Server mit `220 ...`.

## Base64 für Login und Passwort

In der Python-Shell:

```python
import base64
base64.b64encode("RZ-ACCOUNT".encode("utf-8")).decode("utf-8")
base64.b64encode("PASSWORT".encode("utf-8")).decode("utf-8")
```

## SMTP-Dialog

Alle Kommandos klein schreiben (besonders `rcpt to`), sonst interpretiert
OpenSSL ein großes `R` als TLS-Renegotiation und ein großes `Q` als Quit.

```
EHLO meinrechner
AUTH LOGIN
<Base64(Login)>
<Base64(Passwort)>
MAIL FROM:<absender@example.com>
rcpt to:<empfaenger@example.com>
DATA
From: Max Mustermann <mmustermann@htwg-konstanz.de>
To: Max Mustermann <max.mustermann@gmail.com>
Subject: =?utf-8?B?VGVzdG1haWwgYXVzIGRlbSBSTi1MYWJvcg==?=
Date: Wed, 11 Nov 2026 14:00:00 +0100
Message-ID: <20261111140000.4711@htwg-konstanz.de>
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: 8bit

Hallo,
dies ist eine Testmail mit Umlauten: äöü.
.
QUIT
```

Zwischen Header und Text steht eine Leerzeile. Die Mail endet mit einer
Zeile, die nur einen Punkt enthält.

## Was fällt auf?

`MAIL FROM` und das `From:`-Headerfeld sind unabhängig voneinander. Der
SMTP-Umschlag (MAIL FROM/RCPT TO) bestimmt die Zustellung, der Header nur die
Anzeige im Mailprogramm. Deshalb lassen sich Absenderangaben im Header leicht
fälschen (Spoofing). Die Mailserver ergänzen beim Versand unter anderem
`Received`, `Authentication-Results`, `DKIM-Signature`, `Return-Path` und
teilweise `SPF`-Informationen. Bei Gmail kommen zusätzlich `ARC`-Header hinzu.
