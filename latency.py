#!/usr/bin/env python3
"""Rank AWS regions from the SJSU CMPE 273 Spring 2017 quiz by ICMP latency.

Original script: github.com/vanarp96/273-Quiz-1 (February 2017), now
github.com/pranavprem/273-Quiz-1. It was Python 2, asked "PC or Mac?", and
parsed that platform's ping summary. This version runs on Python 3 and picks
the ping flags from the operating system.
"""

from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from typing import TypedDict


class Host(TypedDict):
    name: str
    ip: str


class ProbeResult(TypedDict):
    name: str
    average: float
    line: str


# One ICMP target per AWS region from the Spring 2017 quiz. Each address is
# still published for that prefix on http://ec2-reachability.amazonaws.com/.
# Regions AWS added later are intentionally not included.
HOSTS: list[Host] = [
    {"name": "North California", "ip": "50.18.56.1"},
    {"name": "North Virginia", "ip": "23.23.255.255"},
    {"name": "Ireland", "ip": "34.248.60.213"},
    {"name": "Tokyo", "ip": "13.112.63.251"},
    {"name": "Frankfurt", "ip": "35.156.63.252"},
    {"name": "London", "ip": "52.56.34.0"},
    {"name": "Singapore", "ip": "46.51.216.14"},
    {"name": "Seoul", "ip": "52.78.63.252"},
    {"name": "Ohio", "ip": "52.14.64.0"},
    {"name": "Oregon", "ip": "35.160.63.253"},
    {"name": "Mumbai", "ip": "35.154.63.252"},
    {"name": "Sao Paulo", "ip": "52.67.255.254"},
    {"name": "Sydney", "ip": "13.54.63.252"},
    {"name": "Central Canada", "ip": "52.60.50.0"},
    {"name": "GovCloud US WEST", "ip": "52.222.9.163"},
]

# Backstop so a stuck ping cannot hang the whole quiz run.
PING_TIMEOUT_SECONDS = 25


def ping_command(ip: str) -> list[str]:
    """Build a three-probe ping command for this operating system.

    Windows uses ``-n`` and a millisecond ``-w``. Linux ``-W`` is in seconds.
    macOS and the BSDs take ``-W`` in milliseconds. Five seconds is long
    enough for a distant region and short enough that a dead address does
    not stall the run for the platform default.
    """
    system = platform.system()
    if system == "Windows":
        return ["ping", "-n", "3", "-w", "5000", ip]
    if system == "Linux":
        return ["ping", "-c", "3", "-W", "5", ip]
    return ["ping", "-c", "3", "-W", "5000", ip]


def parse_average(line: str) -> float | None:
    """Return the average RTT in milliseconds from one ping summary line.

    Unix (Linux, macOS, and BusyBox) puts min/avg/max after ``=``.
    Windows prints ``Average = <ms>ms``. Windows reports sub-millisecond
    replies as ``<1ms``; that is treated as 0.5 so it still sorts first.
    """
    if "Average" in line:
        return _parse_windows_average(line)
    if "avg" in line and "=" in line:
        return _parse_unix_average(line)
    return None


def _parse_unix_average(line: str) -> float | None:
    stats = line.split("=", 1)[1].strip()
    if not stats:
        return None
    numbers = stats.split()[0].split("/")
    # min/avg/max[/mdev]. The average is the second field.
    if len(numbers) < 2:
        return None
    try:
        return float(numbers[1])
    except ValueError:
        return None


def _parse_windows_average(line: str) -> float | None:
    tail = line.split("Average", 1)[1]
    if "=" not in tail or "ms" not in tail.lower():
        return None
    number = tail.split("=", 1)[1]
    number = number.lower().split("ms", 1)[0].replace(" ", "")
    if number == "<1":
        return 0.5
    try:
        return float(number)
    except ValueError:
        return None


def probe(host: Host) -> ProbeResult | None:
    """Ping one host. Return None when it does not answer or cannot be parsed."""
    try:
        completed = subprocess.run(
            ping_command(host["ip"]),
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=PING_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None

    for line in completed.stdout.splitlines():
        average = parse_average(line)
        if average is not None:
            return {"name": host["name"], "average": average, "line": line.strip()}
    return None


def collect(hosts: list[Host]) -> tuple[list[ProbeResult], list[Host]]:
    """Probe every host. Successes are sorted fastest first; failures stay in order."""
    results: list[ProbeResult] = []
    missed: list[Host] = []
    for host in hosts:
        print(f"Pinging {host['name']} ({host['ip']})...", file=sys.stderr)
        result = probe(host)
        if result is None:
            missed.append(host)
        else:
            results.append(result)
    results.sort(key=lambda item: item["average"])
    return results, missed


def main() -> int:
    if shutil.which("ping") is None:
        print("ping was not found on PATH.", file=sys.stderr)
        return 1

    system = platform.system()
    if system == "Windows":
        kind = "Windows"
    elif system == "Darwin":
        kind = "Mac"
    else:
        kind = system
    # Flush so the banner is not stuck behind a block-buffered stdout while
    # the pings (progress on stderr) are already running.
    print(
        f"Detected {kind}. Please wait for all pings to complete. "
        "This could take a while.",
        flush=True,
    )

    results, missed = collect(HOSTS)
    for result in results:
        print(f"{result['name']} --- {result['line']}")
    for host in missed:
        print(f"{host['name']} --- no reply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
