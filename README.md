# Asset Watcher
Using this tool you can watch for new assets from Bug Bounty platforms

### What does it watch for?
- When a new program adds to Bug Bounty platforms

- When a program gets Enabled after it was disabled

- When Bounty Payout for a program or asset gets changed

- When a new asset gets added to program scope


### Prerequisites
Python3.6+

python -m pip install requests

### How To Use?
Change "mUrl" variable on line.7 of code and update it with your "Discord WebHook URL"

Run the code --> python3.8 programWatcher.py


### How to schedule the code?
If you are on linux, add this line to your "crontab -e":
```
0 */1 * * * python[Version] /path/to/code/assetWatch.py
```

### More Info
This tool will create a local json database named "watchList.json" and will use this file to watch for new assets
Whenever a new assets gets popped up, you will get a notification on your discord channel
