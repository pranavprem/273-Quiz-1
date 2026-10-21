"""Parser and ranking tests. Live AWS pings are intentionally not required."""

import subprocess

import pytest

import latency


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("rtt min/avg/max/mdev = 62.089/62.089/62.089/0.000 ms", 62.089),
        (
            "round-trip min/avg/max/stddev = 10.123/11.456/12.789/0.123 ms",
            11.456,
        ),
        ("round-trip min/avg/max = 0.215/0.431/0.800 ms", 0.431),
        ("    Minimum = 11ms, Maximum = 12ms, Average = 11ms", 11.0),
        ("Average = <1ms", 0.5),
        ("Average=<1ms", 0.5),
        ("Average = < 1ms", 0.5),
        ("rtt min/avg/max/mdev = nope/nope/nope/nope ms", None),
        ("64 bytes from 1.1.1.1: icmp_seq=1 ttl=55 time=3.12 ms", None),
        ("3 packets transmitted, 0 received, 100% packet loss", None),
        ("", None),
    ],
)
def test_parse_average(line, expected):
    assert latency.parse_average(line) == expected


@pytest.mark.parametrize(
    ("system", "expected"),
    [
        ("Linux", ["ping", "-c", "3", "-W", "5", "203.0.113.10"]),
        ("Darwin", ["ping", "-c", "3", "-W", "5000", "203.0.113.10"]),
        ("FreeBSD", ["ping", "-c", "3", "-W", "5000", "203.0.113.10"]),
        ("Windows", ["ping", "-n", "3", "-w", "5000", "203.0.113.10"]),
    ],
)
def test_ping_command(monkeypatch, system, expected):
    monkeypatch.setattr(latency.platform, "system", lambda: system)
    assert latency.ping_command("203.0.113.10") == expected


def test_probe_reads_summary_line(monkeypatch):
    def fake_run(cmd, **kwargs):
        assert cmd[-1] == "203.0.113.10"
        assert kwargs["timeout"] == latency.PING_TIMEOUT_SECONDS
        completed = subprocess.CompletedProcess(cmd, 0)
        completed.stdout = "PING x\nrtt min/avg/max/mdev = 1/2.5/3/0.1 ms\n"
        completed.stderr = ""
        return completed

    monkeypatch.setattr(latency.subprocess, "run", fake_run)
    result = latency.probe({"name": "Test", "ip": "203.0.113.10"})
    assert result == {
        "name": "Test",
        "average": 2.5,
        "line": "rtt min/avg/max/mdev = 1/2.5/3/0.1 ms",
    }


def test_probe_timeout_is_a_miss(monkeypatch):
    def fake_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="ping", timeout=25)

    monkeypatch.setattr(latency.subprocess, "run", fake_run)
    assert latency.probe({"name": "Test", "ip": "203.0.113.10"}) is None


def test_collect_sorts_fastest_first_and_keeps_misses(monkeypatch):
    hosts = [
        {"name": "Slow", "ip": "1.1.1.1"},
        {"name": "Gone", "ip": "2.2.2.2"},
        {"name": "Fast", "ip": "3.3.3.3"},
    ]

    def fake_probe(host):
        if host["name"] == "Gone":
            return None
        average = 50.0 if host["name"] == "Slow" else 5.0
        return {"name": host["name"], "average": average, "line": f"avg {average}"}

    monkeypatch.setattr(latency, "probe", fake_probe)
    results, missed = latency.collect(hosts)
    assert [item["name"] for item in results] == ["Fast", "Slow"]
    assert [item["name"] for item in missed] == ["Gone"]


def test_main_prints_ranked_results_then_misses(monkeypatch, capsys):
    monkeypatch.setattr(latency.platform, "system", lambda: "Linux")
    monkeypatch.setattr(
        latency,
        "collect",
        lambda hosts: (
            [
                {
                    "name": "Ohio",
                    "average": 20.0,
                    "line": "rtt min/avg/max/mdev = 19/20/21/1 ms",
                },
                {
                    "name": "Tokyo",
                    "average": 100.0,
                    "line": "rtt min/avg/max/mdev = 99/100/101/1 ms",
                },
            ],
            [{"name": "Seoul", "ip": "52.78.63.252"}],
        ),
    )

    assert latency.main() == 0
    out = capsys.readouterr().out
    assert "Detected Linux" in out
    assert out.index("Ohio ---") < out.index("Tokyo ---")
    assert "Ohio --- rtt min/avg/max/mdev = 19/20/21/1 ms" in out
    assert "Seoul --- no reply" in out


def test_main_reports_a_missing_ping_binary(monkeypatch, capsys):
    monkeypatch.setattr(latency.shutil, "which", lambda _name: None)
    assert latency.main() == 1
    assert "ping" in capsys.readouterr().err.lower()


def test_localhost_probe():
    result = latency.probe({"name": "localhost", "ip": "127.0.0.1"})
    if result is None:
        pytest.skip("localhost did not answer ICMP")
    assert result["name"] == "localhost"
    assert result["average"] >= 0
    assert "avg" in result["line"] or "Average" in result["line"]
