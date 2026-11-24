# The World on Tuesday — 24 November 2026

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/rendyhermawan22222-source/makefun-news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/rendyhermawan22222-source/makefun-news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

A one-page newspaper front page summing up the world's news of Tuesday,
24 November 2026. The lead is the overnight Russian strike that flattened
a five-storey block in Zaporizhzhia — at least 2 killed, 40+ hurt, four of
them children — beside a second strike on the Kerch Bridge, where a 227-m
road arch span collapsed into the strait, and the Asian market rebound, with
the Taiex posting its largest point gain on record. Below them, four picture
stories: Pakistan's first astronaut heading for Tiangong, Russian jets
entering Korea's air-defence zone, German business confidence at a
three-year high, and Sanofi's $41bn cash deal for Insmed. Eleven more briefs
round out the day — the Nepal quake, hacked Rosstat death records, strikes
on Ukraine's power grid, the Patriot interceptor wait, a Chinese spy death
sentence, the Megaspeed blacklist, the Pentagon's rebuke of Canada, Gaza,
measles in Pennsylvania, Somalia and Trump's execution push — plus sixteen
one-liners, a UTC timeline, a numbered world map, the numbers of the day, a
sport strip and a date check that keeps Monday's news (and Wednesday's
launches and results) off the page. All fourteen illustrations are original
drawings made in code, not photographs.

## Files

- `entry.png` — the finished front page (1024×1024, PNG).
- `main.py` — verifies `entry.png` against its SHA-256 and copies it to
  the output directory.
- `build/compose.py` — draws the page from scratch with Pillow; re-running
  it reproduces `entry.png` byte for byte.
- `LICENSE` — MIT.

## Run it

```sh
# Re-draw the page (needs Pillow):
python3 build/compose.py

# Publish it the way the grader does:
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` refuses to copy the image if its hash does not match the value
recorded inside it, so a stale or altered `entry.png` can never slip
through. The entry is for the make.fun competition
[news-image-20261124](https://make.fun/c/news-image-20261124).
