#!/usr/bin/env python3
"""
sms_delivery.py — SMS/MMS Delivery via Twilio
Sends SMS messages and (optionally) MMS with media attachments.
Requires TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER env vars.
"""

import os
import sys
import argparse
from colorama import init, Fore, Style

init(autoreset=True)

try:
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException
except ImportError:
    print(Fore.RED + "[-] twilio not installed. Run: pip3 install twilio")
    sys.exit(1)


def banner():
    print(Fore.MAGENTA + """
╔══════════════════════════════════════╗
║       SMS/MMS Delivery Tool         ║
║        Twilio-Based Payload         ║
║   Authorized Security Assessment    ║
╚══════════════════════════════════════╝
""" + Style.RESET_ALL)


def send_sms(to_number: str, message: str, media_url: str = None):
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    from_number = os.environ.get("TWILIO_FROM_NUMBER")

    if not all([account_sid, auth_token, from_number]):
        print(Fore.RED + "[-] Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_FROM_NUMBER")
        sys.exit(1)

    client = Client(account_sid, auth_token)

    try:
        print(f"[*] Sending to: {to_number}")
        print(f"[*] From: {from_number}")
        print(f"[*] Message: {message}")

        kwargs = {
            "to": to_number,
            "from_": from_number,
            "body": message,
        }

        if media_url:
            kwargs["media_url"] = [media_url]
            print(f"[*] Media URL: {media_url}")
            print(Fore.YELLOW + "[*] Sending as MMS with media attachment...")
        else:
            print(Fore.YELLOW + "[*] Sending as plain SMS...")

        # Send the message
        msg = client.messages.create(**kwargs)

        print(Fore.GREEN + f"[+] Message sent successfully!")
        print(Fore.GREEN + f"[+] SID: {msg.sid}")
        print(Fore.GREEN + f"[+] Status: {msg.status}")
        print(Fore.GREEN + f"[+] Price: {msg.price if msg.price else 'Pending'}")

        return msg

    except TwilioRestException as e:
        print(Fore.RED + f"[-] Twilio error: {e}")
        if e.code == 21610:
            print(Fore.YELLOW + "[!] Number is on the do-not-contact list or opted out")
        elif e.code == 21211:
            print(Fore.YELLOW + "[!] Invalid 'To' phone number")
        elif e.code == 21614:
            print(Fore.YELLOW + "[!] Number is unable to receive SMS/MMS")
        elif e.code == 21408:
            print(Fore.YELLOW + "[!] MMS not supported for this region/carrier")
        elif e.code == 20003:
            print(Fore.YELLOW + "[!] Authentication error — check TWILIO_ACCOUNT_SID and AUTH_TOKEN")
        return None

    except Exception as e:
        print(Fore.RED + f"[-] Unexpected error: {e}")
        return None


def main():
    banner()
    parser = argparse.ArgumentParser(description="SMS/MMS Delivery Tool")
    parser.add_argument("to", help="Target phone number (E.164 format, e.g., +15096149539)")
    parser.add_argument("--message", "-m", default="Hey! Check out this video I found 😄",
                        help="SMS message body")
    parser.add_argument("--media", "-media", help="Public URL of media file (for MMS)")
    args = parser.parse_args()

    send_sms(args.to, args.message, args.media)


if __name__ == "__main__":
    main()
