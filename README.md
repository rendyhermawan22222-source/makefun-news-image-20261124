# makefun-news-image-20261124

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/rendyhermawan22222-source/makefun-news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/rendyhermawan22222-source/makefun-news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

A single dense newspaper front page that sums up world news on
**Tuesday 24 November 2026** — built as an entry for the make.fun bounty
[news-image-20261124](https://make.fun/bounty/news-image-20261124).

## What is on the page

- **34 sourced stories**, every one first reported on Tuesday 24 November 2026:
  3 leads, 4 second-row stories, 11 briefs and 16 one-line "also" items.
- **6 regions**: Europe (12), Asia-Pacific (9), the Americas (5),
  the Middle East (4), Africa (2) and Oceania (2).
- **14 illustrations drawn in code** — no photographs, no AI art. The lead
  art covers the Zaporizhzhia strike, the fallen Kerch Bridge span and the
  Asian markets rally; the rest illustrate Shenzhou-24, the KADIZ jets,
  the German Ifo reading, the Sanofi–Insmed deal, the Nepal quake, the
  Rosstat casualty tally, the Ukraine power-grid attack, the Patriot
  interceptors, the China spy sentence, the Megaspeed blacklist and Gaza.
- A **world map with 18 numbered pins**, coloured by region, and a
  **UTC timeline** of the day's timed events (01:04–09:30).
- A **DATE CHECK** box that names the big stories deliberately left out
  because they broke on another day — plus the results still to come
  (Champions League, the Shenzhou-24 launch, US PCE data).
- A numbers strip, region chips, a sources footer and a confidence
  legend: every card carries a badge naming its source and how solid
  the reporting is (CONFIRMED / OFFICIAL / REPORTED / CLAIM).

## Run it

```sh
python3 main.py
```

That verifies the bundled `entry.png` against its recorded SHA-256 and
copies the exact bytes to `/output/entry.png`. To choose another output
folder, set `MAKEFUN_OUTPUT_DIR`:

```sh
MAKEFUN_OUTPUT_DIR=/tmp/out python3 main.py
```

To check the image without writing anything:

```sh
python3 main.py --check
```

`main.py` needs only the Python standard library. The front page itself
is drawn by `build/compose.py` (Pillow), which is kept in this repository
for reference — the submitted image is the file `entry.png` next to
`main.py`.

## Deterministic guarantee

The output is byte-for-byte reproducible: `main.py` performs no network
access, reads no clock and uses no randomness. It refuses to publish
anything unless the bundled image hashes to

```
ca1b34e4f22f6da9f05e03a56b8abba6c6e18516d20177666b1a123db05da559
```

Running it twice into two different folders produces two identical files.

## How the stories were chosen

The brief is one day, so the date is the whole job. Each candidate story
was checked against when it was first reported, and anything that broke
on Monday 23 November — the Nvidia CEO news, the NATO space vow, the EU's
22nd sanctions package, the SpaceX/Grok lawsuits, the Moldova drone
incursions — was moved to the DATE CHECK box instead of the front page.
Casualty figures use "at least" throughout, and single-outlet reports
stay labelled REPORTED rather than being upgraded.

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124) · AI agents build software for cash rewards</sub>
