#!/usr/bin/env python3

"""Fetch the current Ghost Network using fixed placeholder auth headers.

This script is intentionally simple. It does not derive or request any real
auth values. It sends hard-coded "1" values for:

    OS-AuthTicketData
    OS-SessionInfo
    OS-UID
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import time

import requests


APP_ID = "337000"
ENDPOINT = "GhostNetworks_GetTodaysGhostNetwork"
FIXED_VALUE = "1"
LOOP_INTERVAL_SECONDS = 86400
RETRY_INTERVAL_SECONDS = 900


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch the current Ghost Network with fixed header values."
    )
    parser.add_argument(
        "output_dir",
        type=Path,
        nargs="?",
        help="Directory where the fetched Ghost Network JSON will be stored.",
    )
    parser.add_argument(
        "--endpoint",
        default=ENDPOINT,
        help=f"Endpoint to call. Defaults to {ENDPOINT}.",
    )
    parser.add_argument(
        "--loop",
        action="store_true",
        help="Keep running and fetch the network every 24 hours.",
    )
    return parser.parse_args()


def build_headers() -> dict[str, str]:
    return {
        "Accept": "application/json",
        "Accept-Charset": "UTF-8",
        "Host": "dxbreach.os.eidos.com:443",
        "Accept-Encoding": "identity;q=0.9, gzip;q=1.0",
        "Cache-Control": "max-age=0",
        "Content-Type": "application/json",
        "DX-ClientVersion": "8",
        "DataServiceVersion": "2.0",
        "MaxDataServiceVersion": "2.0",
        "OS-Age": "0",
        "OS-AuthProvider": "1",
        "OS-AuthTicketData": FIXED_VALUE,
        "OS-AuthTicketSize": str(len(FIXED_VALUE)),
        "OS-Build": "v1.19 build 801.0",
        "OS-Dest": "prodnet",
        "OS-GTime": "15",
        "OS-Locale": "en,US,US,Liberty Island",
        "OS-OSVersion": "5.1.40.91562",
        "OS-PID": "DXNG-4.0",
        "OS-Platform": "steam",
        "OS-Progress": "0.00000000000000000",
        "OS-SID": "04510451-0451-0451-0451-045104510451",
        "OS-SessionInfo": FIXED_VALUE,
        "OS-STime": "451",
        "OS-System": "windows",
        "OS-TitleID": APP_ID,
        "OS-UID": FIXED_VALUE,
        "OS-XYZ": "0.00000000000000000,0.00000000000000000,0.00000000000000000",
        "OS-Zone": "breach_master",
        "User-Agent": "OS/5.1.40/windows/official",
    }


def fetch_ghost_network(output_dir: Path | None, endpoint: str) -> tuple[bytes, Path | None]:
    headers = build_headers()
    user_id = headers["OS-UID"]
    response = requests.get(
        url=(
            f"https://dxbreach.os.eidos.com/game/{endpoint}"
            f"?s_characterSlotId=breach&s_userId={user_id}"
        ),
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()

    payload = response.content
    ghost_network = json.loads(payload)
    if "d" not in ghost_network or "c_dto" not in ghost_network["d"]:
        raise RuntimeError(f"Bad response data: {payload!r}")

    if output_dir is None:
        return payload, None

    network_date = ghost_network["d"]["c_dto"]["dto_ghostNetworkDate"][15:25]
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", network_date) is None:
        raise RuntimeError(f"Bad ghost network date: {network_date!r}")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{network_date}.json"
    output_path.write_bytes(payload)
    return payload, output_path


def main() -> int:
    args = parse_args()
    while True:
        try:
            payload, output_path = fetch_ghost_network(args.output_dir, args.endpoint)
        except requests.RequestException:
            if not args.loop:
                raise
            print(
                f"Request failed. Sleeping {RETRY_INTERVAL_SECONDS} seconds before retry..."
            )
            time.sleep(RETRY_INTERVAL_SECONDS)
            continue

        if output_path is None:
            sys.stdout.buffer.write(payload)
            if not payload.endswith(b"\n"):
                sys.stdout.buffer.write(b"\n")
            sys.stdout.flush()
        else:
            print(f"Saved Ghost Network to {output_path}")

        if not args.loop:
            return 0

        print(f"Sleeping {LOOP_INTERVAL_SECONDS} seconds before next fetch...")
        time.sleep(LOOP_INTERVAL_SECONDS)


if __name__ == "__main__":
    raise SystemExit(main())