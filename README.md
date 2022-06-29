# Update notifier
I notify you if there is an ubuntu update available!

### Install
1. Change the permissions to notify:
```
chmod +x notify.py
```
Move the main directory anywhere you want. Then go to `.bashrc` or `.profile` and append the following line at the end:
```bash
./update-notifier/notify.py
```