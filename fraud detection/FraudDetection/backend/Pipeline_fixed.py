import os
import smtplib
from email.message import EmailMessage
from typing import Any, Dict

# Optional Twilio support for SMS notifications
try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except Exception:
    TWILIO_AVAILABLE = False


def _get_smtp_config():
    return {
        'host': os.environ.get('EMAIL_HOST'),
        'port': int(os.environ.get('EMAIL_PORT', 0)) if os.environ.get('EMAIL_PORT') else None,
        'user': os.environ.get('EMAIL_USER'),
        'password': os.environ.get('EMAIL_PASS'),
        'to': os.environ.get('NOTIFY_EMAIL')
    }


def send_notification(transaction: Any, subject: str = None, body: str = None) -> bool:
    """Send a notification about a suspicious transaction.

    Falls back to printing the message if SMTP or Twilio is not configured.
    Returns True if notification was (attempted) sent, False otherwise.
    """
    cfg = _get_smtp_config()
    # Prepare readable transaction summary
    try:
        # transaction may be list, dict, or pandas Series
        if hasattr(transaction, 'to_dict'):
            tx_summary = transaction.to_dict()
        elif isinstance(transaction, dict):
            tx_summary = transaction
        else:
            # fallback for list/tuple
            tx_summary = {'transaction': transaction}
    except Exception:
        tx_summary = {'transaction': str(transaction)}

    subject = subject or f"Fraud Alert: Suspicious transaction detected"
    body = body or f"Suspicious transaction detected:\n\n{tx_summary}\n\nTake immediate action."

    # Use SMTP if configured
    sent_any = False
    if cfg['host'] and cfg['port'] and cfg['user'] and cfg['password'] and cfg['to']:
        try:
            msg = EmailMessage()
            msg['Subject'] = subject
            msg['From'] = cfg['user']
            msg['To'] = cfg['to']
            msg.set_content(body)

            with smtplib.SMTP(cfg['host'], cfg['port']) as server:
                server.starttls()
                server.login(cfg['user'], cfg['password'])
                server.send_message(msg)

            print(f"✅ Notification sent to {cfg['to']}")
            sent_any = True
        except Exception as e:
            print(f"⚠️ Notification failed (SMTP): {e}")
            print("Falling back to console print for notification.")

    # Try SMS if configured
    twilio_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    twilio_token = os.environ.get('TWILIO_AUTH_TOKEN')
    twilio_from = os.environ.get('TWILIO_FROM')
    notify_phone = os.environ.get('NOTIFY_PHONE')
    if TWILIO_AVAILABLE and twilio_sid and twilio_token and twilio_from and notify_phone:
        try:
            client = TwilioClient(twilio_sid, twilio_token)
            sms = client.messages.create(body=body, from_=twilio_from, to=notify_phone)
            print(f"✅ SMS notification sent to {notify_phone} (sid={sms.sid})")
            sent_any = True
        except Exception as e:
            print(f"⚠️ SMS notification failed: {e}")
            print("Falling back to console print for notification.")

    # Fallback: print the notification if nothing was sent
    if not sent_any:
        print("\n=== FRAUD NOTIFICATION ===")
        print("Subject:", subject)
        print(body)
        print("=== END NOTIFICATION ===\n")

    return True


def block_transaction(transaction: Any) -> Dict[str, Any]:
    """Block the transaction.

    For now, blocking prints a failure message and returns a dict indicating the block.
    In a real system this should integrate with the transaction processor to stop the transfer.
    """
    try:
        if hasattr(transaction, 'to_dict'):
            tx_summary = transaction.to_dict()
        elif isinstance(transaction, dict):
            tx_summary = transaction
        else:
            tx_summary = {'transaction': transaction}
    except Exception:
        tx_summary = {'transaction': str(transaction)}

    message = f"Transaction blocked: {tx_summary}"
    # For audit we print; production should write to a log or DB and stop processing
    print("\n❌ TRANSACTION BLOCKED ❌")
    print(message)
    print("Action: Transaction marked as failed / blocked.\n")

    return {
        'status': 'blocked',
        'message': message
    }


def process_transaction(transaction: Any, fraud_flag: int, fraud_probability: float = None) -> Dict[str, Any]:
    """Process a single transaction based on fraud_flag.

    If fraud_flag is truthy, send notification and block the transaction.
    Returns a dict with action details so callers can include this in responses.
    """
    result = {
        'fraud_flag': int(bool(fraud_flag)),
        'notification_sent': False,
        'blocked': False,
        'message': None
    }

    if int(bool(fraud_flag)) == 1:
        subj = f"Fraud Alert - Transaction Blocked"
        body = f"Fraud probability: {fraud_probability}\nTransaction: {transaction}"
        notified = send_notification(transaction, subject=subj, body=body)
        result['notification_sent'] = bool(notified)
        block_info = block_transaction(transaction)
        result['blocked'] = True
        result['message'] = block_info.get('message')
    else:
        result['message'] = 'Transaction allowed'

    return result
