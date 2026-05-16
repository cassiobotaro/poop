from poop.types.smtplib import LMTP, SMTP, SMTP_SSL, Smtplib

NAMESPACE: dict[str, object] = {
    "smtplib": Smtplib,
    "SMTP": SMTP,
    "SMTP_SSL": SMTP_SSL,
    "LMTP": LMTP,
}
