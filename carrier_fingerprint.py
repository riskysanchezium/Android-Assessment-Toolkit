#!/usr/bin/env python3
"""
carrier_fingerprint.py — Twilio Lookup v2 API Carrier Fingerprinting
Requires TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN env vars.
"""

import os
import sys
import json
from colorama import init, Fore, Style

init(autoreset=True)

try:
    from twilio.rest import Client
except ImportError:
    print(Fore.RED + "[-] twilio not installed. Run: pip3 install twilio")
    sys.exit(1)


def banner():
    print(Fore.CYAN + """
╔══════════════════════════════════════╗
║    Twilio Carrier Fingerprinting    ║
║   Authorized Security Assessment    ║
╚══════════════════════════════════════╝
""" + Style.RESET_ALL)


def lookup_carrier(number: str):
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")

    if not account_sid or not auth_token:
        print(Fore.RED + "[-] Set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN environment variables")
        sys.exit(1)

    client = Client(account_sid, auth_token)

    try:
        print(f"[*] Looking up: {number}")
        phone_number = client.lookups.v2 \
            .phone_numbers(number) \
            .fetch(fields="line_type_info,caller_name,sim_swap")

        print(Fore.GREEN + "[+] Lookup Results:")
        print(json.dumps({
            "country_code": phone_number.country_code,
            "phone_number": phone_number.phone_number,
            "national_format": phone_number.national_format,
            "caller_name": phone_number.caller_name,
            "line_type": phone_number.line_type_intelligence.get("type", "Unknown"),
            "carrier": phone_number.carrier,
        }, indent=2))

        # Parse carrier info
        if phone_number.carrier:
            print(Fore.GREEN + f"[+] Carrier Name: {phone_number.carrier.get('name', 'N/A')}")
            print(Fore.GREEN + f"[+] Carrier Type: {phone_number.carrier.get('type', 'N/A')}")
            print(Fore.GREEN + f"[+] Mobile Country Code (MCC): {phone_number.carrier.get('mobile_country_code', 'N/A')}")
            print(Fore.GREEN + f"[+] Mobile Network Code (MNC): {phone_number.carrier.get('mobile_network_code', 'N/A')}")

        # Line type
        if phone_number.line_type_intelligence:
            lt = phone_number.line_type_intelligence.get("type", "Unknown")
            print(Fore.CYAN + f"[*] Line Type: {lt}")
            if lt == "mobile":
                print(Fore.GREEN + "[+] Confirmed mobile/wireless number — SMS/MMS delivery viable")
            else:
                print(Fore.YELLOW + "[!] Not identified as mobile — may be landline/VoIP")

        # SIM swap info
        if phone_number.sim_swap:
            print(Fore.YELLOW + f"[*] SIM Swap Detected: {phone_number.sim_swap}")

    except Exception as e:
        print(Fore.RED + f"[-] Twilio lookup failed: {e}")
        print(Fore.YELLOW + "[*] Falling back to phonenumbers library...")
        fallback_lookup(number)


def fallback_lookup(number: str):
    """Fallback using phonenumbers if Twilio fails."""
    import phonenumbers
    from phonenumbers import carrier, geocoder

    try:
        parsed = phonenumbers.parse(number, None)
        if phonenumbers.is_valid_number(parsed):
            carr = carrier.name_for_number(parsed, 'en')
            geo = geocoder.description_for_valid_number(parsed, 'en')
            print(Fore.YELLOW + f"[*] Fallback Carrier: {carr or 'Unknown'}")
            print(Fore.YELLOW + f"[*] Fallback Location: {geo or 'Unknown'}")
        else:
            print(Fore.RED + "[-] Invalid number")
    except Exception as e2:
        print(Fore.RED + f"[-] Fallback failed: {e2}")


if __name__ == "__main__":
    banner()
    if len(sys.argv) < 2:
        print("Usage: python3 carrier_fingerprint.py <phone_number>")
        print("Example: python3 carrier_fingerprint.py +15096149539")
        sys.exit(1)

    lookup_carrier(sys.argv[1])
