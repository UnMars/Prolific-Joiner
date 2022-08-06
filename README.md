<p align="center"><img width="200" src="https://github.com/UnMars/Prolific-Joiner/blob/main/media/Prolific_logo.png" alt="Prolific Logo"></p>
<h1 align="center">Prolific Joiner</h1>


Inspired from [@shiflux](https://github.com/shiflux/prolific-updater)'s one.
## Installation
```sh
git clone https://github.com/UnMars/Prolific-Joiner
```

## Requirements
```sh
pip install -r requirements.txt
```

## Usage
```sh
python main.py
```

## Configuration
Edit the settings.json file.

|Config|Usage|
| :------------: | :------------: |
|auto_renew_bearer|"True" or "False" *(default True)*|
|mail|Your mail on Prolific *(used to renew token)*|
|password|Your password on Prolific *(used to renew token)*|
|Prolific_ID|Your Prolific ID|

## Features
- Auto joining new study, generate a notification and open a new tab for it
- Almost all requests based (except for the token renewal)
- ReCaptcha Bypass
- Fast & headless
- Liteweight
- Can run 24/7

## Notes

Please use the bot only when you can be here for the study, don't take place in studies you'll can't do.
Don't spam the API or you'll get banned !
I'm open to every requests, make a PR :raised_hands: !
