#!/usr/bin/env python3
"""
phone_osint.py — Phone Number OSINT Reconnaissance
Uses the phonenumbers library to extract carrier, geo, timezone, and line type info.
"""

import sys
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
from colorama import init, Fore, Style

init(autoreset=True)

def banner():
    print(Fore.CYAN + """
╔══════════════════════════════════════╗
║       Phone OSINT Recon Tool        ║
║   Authorized Security Assessment    ║
╚══════════════════════════════════════╝
""" + Style.RESET_ALL)

def analyze(number: str):
    try:
        parsed = phonenumbers.parse(number, None)
    except phonenumbers.NumberParseException as e:
        print(Fore.RED + f"[-] Parse error: {e}")
        sys.exit(1)

    if not phonenumbers.is_valid_number(parsed):
        print(Fore.RED + "[-] Invalid phone number")
        sys.exit(1)

    print(Fore.GREEN + f"[+] Number: {phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)}")
    print(f"[+] National: {phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)}")
    print(f"[+] E.164: {phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)}")
    print(f"[+] Country Code: +{parsed.country_code}")
    print(f"[+] Country: {geocoder.description_for_number(parsed, 'en')}")
    print(f"[+] Location: {geocoder.description_for_valid_number(parsed, 'en')}")

    tz = timezone.time_zones_for_number(parsed)
    print(f"[+] Timezone(s): {', '.join(tz) if tz else 'N/A'}")

    carr = carrier.name_for_number(parsed, 'en')
    print(f"[+] Carrier: {carr if carr else 'Unknown'}")

    # Number type detection
    num_type = phonenumbers.number_type(parsed)
    type_map = {
        0: "FIXED_LINE",
        1: "MOBILE",
        2: "FIXED_LINE_OR_MOBILE",
        3: "TOLL_FREE",
        4: "PREMIUM_RATE",
        5: "SHARED_COST",
        6: "VOIP",
        7: "PERSONAL_NUMBER",
        8: "PAGER",
        9: "UAN",
        10: "VOICEMAIL",
    }
    print(f"[+] Line Type: {type_map.get(num_type, 'Unknown')}")

    # Carrier-specific notes
    if carr:
        carr_lower = carr.lower()
        if "verizon" in carr_lower:
            print(Fore.YELLOW + "[*] Note: Verizon uses CDMA/LTE — MMS delivery works")
        elif "tmobile" in carr_lower or "t-mobile" in carr_lower:
            print(Fore.YELLOW + "[*] Note: T-Mobile supports MMS, no CDMA limitations")
        elif "att" in carr_lower or "at&t" in carr_lower or "sprint" in carr_lower:
            print(Fore.YELLOW + "[*] Note: Major carrier — MMS compatible")
        else:
            print(Fore.YELLOW + "[*] Note: Verify MMS support for this carrier")

    if parsed.is_possible_number:
        print(Fore.GREEN + "[+] Number is valid and possible")

    return parsed


if __name__ == "__main__":
    banner()
    if len(sys.argv) < 2:
        print("Usage: python3 phone_osint.py <phone_number>")
        print("Example: python3 phone_osint.py +15096149539")
        sys.exit(1)

    number = sys.argv[1]
    analyze(number)
