# 273 Quiz 1 — AWS region latency

A short Python script that pings one address in each AWS region from a Spring 2017 class quiz and prints those regions from lowest round-trip time to highest.

You run it in a terminal. A sample transcript is at the bottom.

## Original context

This is **Quiz 1** from **CMPE 273, Enterprise Distributed Systems**, at San Jose State University, Spring 2017. The GitHub description still reads: "Find Latency for all AWS instances - Quiz1 for CMPE 273 -- SJSU Spring '17". The commits are from the evening of February 1, 2017. The first commit message called the same work "Assignment 1", and a later commit renamed the file to `latency.py` because that was the name the quiz asked for (it had been `python latency.py`).

It was written in Python 2. It asked whether you had a PC or a Mac, then pinged fifteen addresses three times each, pulled the average out of that platform's ping summary, and printed the regions sorted by that average. The source comment pointed at `github.com/vanarp96/273-Quiz-1`, which is where this repo was first published. It now lives at [github.com/pranavprem/273-Quiz-1](https://github.com/pranavprem/273-Quiz-1).

The addresses are the ones checked in with the quiz, one per region that existed in early 2017, including GovCloud US West. They came from Amazon's EC2 reachability list (`http://ec2-reachability.amazonaws.com/`). As of October 2026 those same fifteen addresses are still the published ICMP targets for the prefixes below. Regions AWS opened after the quiz are not in the list, on purpose.

## How it works

1. Detect the operating system and build a three-packet `ping` for each address.
   Windows uses `ping -n 3 -w 5000`. Linux uses `ping -c 3 -W 5` (`-W` is seconds). macOS and the BSDs use `ping -c 3 -W 5000` (`-W` is milliseconds).
2. Read the summary line and take the average RTT.
   - Linux and macOS: the `avg` field in `min/avg/max`, for example `rtt min/avg/max/mdev = 1.3/1.8/2.6/0.5 ms`.
   - Windows: the `Average = …ms` field. A Windows `<1ms` reading counts as 0.5 ms so it still sorts.
3. Sort the regions that answered, fastest first.
4. Print `Name --- <summary line>`. An address that did not answer is listed after the ranking as `Name --- no reply`.

While it runs, each probe is announced on stderr (`Pinging Ohio (52.14.64.0)...`). The ranking stays on stdout, so `python3 latency.py > regions.txt` saves just the results. A full pass is about half a minute when every address answers.

The old script asked you to type `1` for a PC or `2` for a Mac. Anything else, including Linux, either crashed (`ValueError` on a non-numeric answer) or used the wrong ping flags. The operating system is detected now. The ranking and the `Name --- summary` lines are the same idea as the quiz.

## How to run it today

You need Python 3.11 or newer (3.12 is what CI uses) and `ping` on your `PATH`. ICMP to the public addresses below has to be allowed. There is nothing to install to run the script.

```bash
python3 latency.py
```

Tests and lint use two pinned dev tools and no runtime libraries:

```bash
python3 -m pip install -r requirements-dev.txt
ruff check .
ruff format --check .
pytest
```

GitHub Actions runs those three commands on Python 3.12 for every push and pull request.

## Tech stack

- Python 3.11+ standard library (`subprocess`, `platform`, `shutil`)
- The operating system's `ping` (iputils on Linux, BSD ping on macOS, Windows ping)
- [pytest 9.1.1](https://pypi.org/project/pytest/) and [Ruff 0.17.0](https://pypi.org/project/ruff/) for tests and formatting
- GitHub Actions

## Project structure

```
latency.py                 the script
tests/test_latency.py      parser, ping flags, ranking, one localhost ping
requirements-dev.txt       pinned pytest and ruff
pyproject.toml             ruff and pytest settings
.github/workflows/ci.yml   lint and test
AGENTS.md                  notes for coding agents
CLAUDE.md                  pointer to AGENTS.md
```

## Regions

Names are the quiz's names. Region codes are the AWS regions those names refer to. The prefix is the block on the current EC2 reachability list whose published ping address is still the quiz's IP.

| Quiz name | Region | Address | Reachability prefix |
| --- | --- | --- | --- |
| North California | us-west-1 | 50.18.56.1 | 50.18.0.0/16 |
| North Virginia | us-east-1 | 23.23.255.255 | 23.20.0.0/14 |
| Ireland | eu-west-1 | 34.248.60.213 | 34.248.0.0/13 |
| Tokyo | ap-northeast-1 | 13.112.63.251 | 13.112.0.0/14 |
| Frankfurt | eu-central-1 | 35.156.63.252 | 35.156.0.0/14 |
| London | eu-west-2 | 52.56.34.0 | 52.56.0.0/16 |
| Singapore | ap-southeast-1 | 46.51.216.14 | 46.51.216.0/21 |
| Seoul | ap-northeast-2 | 52.78.63.252 | 52.78.0.0/16 |
| Ohio | us-east-2 | 52.14.64.0 | 52.14.0.0/16 |
| Oregon | us-west-2 | 35.160.63.253 | 35.160.0.0/13 |
| Mumbai | ap-south-1 | 35.154.63.252 | 35.154.0.0/16 |
| Sao Paulo | sa-east-1 | 52.67.255.254 | 52.67.0.0/16 |
| Sydney | ap-southeast-2 | 13.54.63.252 | 13.54.0.0/15 |
| Central Canada | ca-central-1 | 52.60.50.0 | 52.60.0.0/16 |
| GovCloud US WEST | us-gov-west-1 | 52.222.9.163 | 52.222.0.0/17 |

## Sample output

From one run on 15 October 2026. These milliseconds are a property of the network the script ran on. Yours will differ, and two runs in a row will not match to the tenth of a millisecond. The stderr `Pinging …` lines are omitted here so the ranking is easy to read.

```text
Detected Linux. Please wait for all pings to complete. This could take a while.
North Virginia --- rtt min/avg/max/mdev = 1.338/1.803/2.598/0.564 ms
Ohio --- rtt min/avg/max/mdev = 13.673/14.190/14.885/0.510 ms
Central Canada --- rtt min/avg/max/mdev = 16.377/16.718/17.268/0.392 ms
GovCloud US WEST --- rtt min/avg/max/mdev = 55.841/56.324/57.156/0.590 ms
North California --- rtt min/avg/max/mdev = 62.655/63.243/64.236/0.705 ms
Oregon --- rtt min/avg/max/mdev = 68.091/68.303/68.637/0.239 ms
Ireland --- rtt min/avg/max/mdev = 69.173/69.859/71.048/0.844 ms
London --- rtt min/avg/max/mdev = 76.078/76.547/77.463/0.647 ms
Frankfurt --- rtt min/avg/max/mdev = 91.302/91.856/92.876/0.721 ms
Sao Paulo --- rtt min/avg/max/mdev = 113.788/114.878/116.978/1.485 ms
Tokyo --- rtt min/avg/max/mdev = 144.771/145.391/146.295/0.653 ms
Seoul --- rtt min/avg/max/mdev = 175.638/176.252/177.125/0.633 ms
Mumbai --- rtt min/avg/max/mdev = 185.819/186.421/187.336/0.657 ms
Singapore --- rtt min/avg/max/mdev = 218.689/219.000/219.610/0.430 ms
Sydney --- rtt min/avg/max/mdev = 220.277/220.974/222.054/0.774 ms
```

## Limits

- The number you get is ICMP round-trip time to that reachability address.
- The region list is the early 2017 quiz list. AWS regions opened later are left out.
- A `no reply` line means that address did not answer from your network. AWS can rate-limit these probes.
- Ping text is assumed to be English (`avg` or `Average`).
