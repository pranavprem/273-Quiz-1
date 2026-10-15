# Agent guide

`latency.py` is the whole program. It is a Spring 2017 SJSU CMPE 273 quiz: ping
the 15 AWS addresses in `HOSTS`, read each average RTT, and print the regions
fastest first. History and how to run it are in [README.md](README.md). This
file is the working notes. Do not copy it into `CLAUDE.md` or `.cursor/rules`.

## Layout

- `latency.py` — hosts, ping command, summary parser, ranking, and CLI.
- `tests/test_latency.py` — parser, command flags, ranking, and one localhost ping.
- `requirements-dev.txt` — pinned pytest and ruff. No runtime dependencies.
- `pyproject.toml` — ruff and pytest settings only.
- `.github/workflows/ci.yml` — lint and tests on Python 3.12.

There is no package, no UI, and no license file. Do not add a license.

## Commands

Requires Python 3.11 or newer and `ping` on `PATH`.

```bash
python3 latency.py
python3 -m pip install -r requirements-dev.txt
ruff check .
ruff format .
pytest
```

## Conventions

- Keep the script runnable as `python3 latency.py`. The quiz required that filename.
- Standard library only at runtime. Do not add a dependency for ping, CLI parsing, or sorting.
- Rank by the average on the ping summary line, not by a hand-rolled timer.
- Successful lines stay `Name --- <raw summary>`. Unanswered hosts stay `Name --- no reply` after the ranking, in list order.
- Progress goes to stderr so stdout stays the ranking.
- New behavior needs a unit test that does not contact AWS. Mock `subprocess.run`.
- Format with ruff. Target Python 3.11. Line length 88.

## Gotchas

- The host list is the quiz list. Every address was still on
  `http://ec2-reachability.amazonaws.com/` for its original region when this
  was refreshed. Do not swap in newer regions or "cleaner" IPs unless asked.
  A `no reply` means that address did not answer from here, not that the region is down.
- Linux `ping -W` is seconds. macOS and BSD `ping -W` are milliseconds.
  Windows uses `ping -n` and `ping -w` in milliseconds. Getting this wrong
  makes every host look dead, or makes the script wait thousands of seconds.
- The old script was Python 2 (`raw_input`, statement `print`) and asked the
  user to choose PC or Mac. Linux had no working path, and a non-numeric
  answer raised `ValueError`. Do not bring that prompt back.
- Parsing assumes English ping text (`avg` / `Average`). A localized Windows
  ping will be reported as `no reply`.
- Windows prints sub-millisecond RTTs as `<1ms`. The parser uses 0.5 so the
  value still sorts. Do not let that string reach `float()` uncaught.
- Do not call `ping` through `shell=True`.
- Tests must not ping the public AWS addresses. The localhost test may skip
  when ICMP to `127.0.0.1` is blocked.
- No secrets belong in this repo. The addresses are public reachability targets.

## Leave alone

- The 15 names and addresses, including the original spelling (`Sao Paulo`, `GovCloud US WEST`).
- Three pings per region, then a sort by average.
- Printing the summary line itself, not a reformatted table.
- ICMP. This quiz did not measure TCP or HTTP latency.
