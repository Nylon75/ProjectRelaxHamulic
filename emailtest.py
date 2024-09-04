import smtplib
from email.mime.text import MIMEText

def send_test_email():
    sender = "Relax.Hamulic@gmail.com"
    recipient = "hamuliccazin38@gmail.com"
    password = "tcaornolambznhkb"  # Das 16-stellige App-Passwort

    msg = MIMEText("Dies ist eine Test-E-Mail.")
    msg['Subject'] = "Test E-Mail"
    msg['From'] = sender
    msg['To'] = recipient

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
        print("E-Mail erfolgreich gesendet!")
    except Exception as e:
        print(f"Fehler beim Senden der E-Mail: {e}")

send_test_email()