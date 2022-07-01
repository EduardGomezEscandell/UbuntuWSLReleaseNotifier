# Update notifier
I notify you if there is an ubuntu update available!

### Install
1. Change the permissions to notify:
```bash
chmod +x notify.py
```
Go to `.bashrc` or `.profile` and append the following line at the end:
```bash
${HOME}/path-to-repository/notify.py --frequency=daily
```
If you have high latency, you can increase the max timeout.
```bash
${HOME}/path-to-repository/notify.py --frequency=daily --timeout=<SECONDS>
```
