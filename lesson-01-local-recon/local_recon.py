#!/usr/bin/env python3
"""
Lesson 01: Local Recon Practical
Safe target: 127.0.0.1 only.
Purpose: understand network interfaces, listening services, HTTP headers, and simple TCP connect scanning.
"""

import socket
import subprocess
import urllib.request
from datetime import datetime, timezone

TARGET = "127.0.0.1"
PORTS = [22, 53, 80, 443, 8000, 8080, 8081, 8888]


def run(cmd):
    print(f"\n$ {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, text=True, capture_output=True, timeout=10)
        if result.stdout:
            print(result.stdout.strip())
        if result.stderr:
            print(result.stderr.strip())
        print(f"exit_code={result.returncode}")
    except Exception as e:
        print(f"ERROR: {e}")


def scan_port(host, port, timeout=0.4):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        code = sock.connect_ex((host, port))
        return code == 0
    finally:
        sock.close()


def grab_http_headers(url):
    print(f"\nHTTP header grab: {url}")
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=5) as response:
            print(f"Status: {response.status} {response.reason}")
            for key, value in response.headers.items():
                print(f"{key}: {value}")
    except Exception as e:
        print(f"ERROR: {e}")


def main():
    print("=" * 70)
    print("Lesson 01: Local Recon Practical")
    print(f"Time UTC: {datetime.now(timezone.utc).isoformat()}")
    print(f"Target: {TARGET} only")
    print("=" * 70)

    run(["ip", "-br", "addr"])
    run(["ip", "route"])
    run(["ss", "-tulnp"])

    print("\nSimple TCP connect scan")
    for port in PORTS:
        state = "open" if scan_port(TARGET, port) else "closed/filtered"
        print(f"{TARGET}:{port:<5} {state}")

    grab_http_headers(f"http://{TARGET}:8080/")

    print("\nAnalyst notes:")
    print("- Open ports represent reachable services and potential attack surface.")
    print("- Service banners/headers can reveal technologies and versions.")
    print("- Defenders can detect scanning using connection telemetry, firewall logs, Sysmon Event ID 3, or SIEM network logs.")


if __name__ == "__main__":
    main()
