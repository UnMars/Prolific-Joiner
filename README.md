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
Edit the config.json file.

|Config|Usage|
| :------------: | :------------: |
|auto_renew_bearer|"True" or "False" *(default True)*|
|stop_on_idle|"True" or "False" *(default True)*|
|mail|Your mail on Prolific *(used to renew token)*|
|password|Your password on Prolific *(used to renew token)*|
|Prolific_ID|Your Prolific ID|

## Known Error Code

|Error Code|Details|Meaning
| :------------: | :------------: | :------------: |
|140010|PEC-SUB-0002: We are sorry but we could not create your submission at this time. This may be due to your current network connection. For more information please see our <a href="https://participant-help.prolific.co/hc/en-gb/articles/360012393100-PEC-Error">help centre article</a>.|https://participant-help.prolific.co/hc/en-gb/articles/360012393100-PEC-Error#heading-0 <br /> **The IP address that you are using was flagged for suspicious behaviour** </br> Either wait for it to resolve by itself or make a ticket to Prolific Support. <br /> *(Try also to raise sleep duration)*



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
