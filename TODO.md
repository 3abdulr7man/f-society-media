# TODO - F-SOCIETY YT-DLP TOOL (single-file) 

## Step 1 — Refactor `yt_dlp_tool.py`
- [ ] Replace simplistic implementation with full interactive menu
- [ ] Add settings persistence (settings.json runtime created)
- [ ] Add history capped to last 50 entries
- [ ] Add logging (logs.jsonl) and export capability

## Step 2 — Download engine upgrades
- [ ] Implement video download with format presets (144p→4K), merging, resume, concurrency fragments
- [ ] Implement audio download with bitrate selection (48–320 kbps)
- [ ] Implement images and gallery batch download modes
- [ ] Implement smart fallback between codecs/resolutions when selected format fails
- [ ] Implement retry mechanism + actionable error messages

## Step 3 — Queue & concurrency manager
- [ ] Add queue add/clear/list
- [ ] Implement batch start with max concurrent downloads from settings

## Step 4 — Platform detection + metadata display
- [ ] Expand platform detection and show platform-specific metadata

## Step 5 — Update system & checks
- [ ] Add yt-dlp update via pip with Python version/ffmpeg checks

## Step 6 — BAT launcher
- [ ] Update `run.bat` to use `python -u` and pass through args if desired

## Step 7 — Verification
- [ ] Test video download
- [ ] Test audio download (bitrate)
- [ ] Test thumbnail/images
- [ ] Test history/queue/settings persistence
- [ ] Test logging export

