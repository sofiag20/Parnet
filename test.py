# test_smtp.py
import smtplib
from email.mime.text import MIMEText

SERVER = 'smtp.gmail.com'
PORT   = 587
USER   = 'parnetoficial@gmail.com'
PASS   = 'gfss tlhm nhpb dvde'
TO     = 'parnetoficial@gmail.com'

msg = MIMEText("Este es un correo de prueba", _charset='utf-8')
msg['Subject'] = 'Prueba SMTP'
msg['From']    = USER
msg['To']      = TO

with smtplib.SMTP(SERVER, PORT) as s:
    s.starttls()
    s.login(USER, PASS)
    s.send_message(msg)
print("Correo de prueba enviado")
