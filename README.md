# Datadog Controller
Do you have (or are going to have) a lot of Datadog screenboards and have no idea how to deal with that? This tool helps to:

* initially migrate off all the settings were done in Datadog UI to YaML configs in your GIT repo in a compact format
* compare existing screenboards and monitors in Datadog UI with your local configs and their local changes
* update or create screenboards and monitors via `vim` and command line

## Additional features
* Move a common part of screenboard widgets and monitors into a special section of common settings to make a config file significantly shorter
* Work with monitors by name instead of id
* Replace a link to screenboard in monitor description to `https://app.datadoghq.com/screen/<screenboard-id>` on read and vise versa on update
* Work in safe mode with `--update-only` flag: only update the existing records without inserts

## How to automate your screenboard?
1. Read a remote config via "read" command and save it to a file:
    `./main.py read -s 'HelloWorld Production' > hw-prod-screenboard.yml`
2. Automate generation of this file on your own. You also can use [j2cli](https://github.com/kolypto/j2cli).
3. Check that a generated file equals to your configuration in UI via "compare" command:
    `./main.py compare hw-prod-screenboard.yml -s 'HelloWorld Production'`
4. Update the remote config according to a local config file:
    `./main.py update hw-prod-screenboard.yml`

## Limitations
* The tool works with monitors names. To change a monitor name you should do that manually both in a local config and in Datadog UI to save consistency.

## Installation
    sudo pip install -r requirements.txt

## See also
* [Developer documentation](DEV.md)
* [To-do list](TODO.md)
