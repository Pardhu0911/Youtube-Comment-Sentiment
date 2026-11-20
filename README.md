# YouTube comment sentiment

This script groups YouTube comments by sentiment and draws a stacked bar chart for each video. It uses TextBlob to label each comment positive, neutral or negative.

**Pardha Saradhi Edupalli** · University of Cincinnati

## Try the offline example

Run these commands in PowerShell from this project folder with Python 3.12 installed.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python sentiment.py
```

Open `sentiment.png` to view the result. The included CSV has eight fictional comments across two videos. The script counts each sampled comment once and skips videos with comments disabled. TextBlob is an English-language baseline and can misread sarcasm, slang and other languages.

## Analyze current videos

Enable YouTube Data API v3 for your Google project. Supply your own restricted key through the local `YOUTUBE_API_KEY` environment variable, then run `.\.venv\Scripts\python sentiment.py --live`. The program prints aggregate counts and saves a chart in the working folder.

Live mode samples up to 20 top-level comments apiece from ten popular US videos. The chart summarizes that sample. It can’t tell you how everyone who watched the video felt.

Copyright © 2026 Pardha Saradhi Edupalli. [MIT license](LICENSE)
