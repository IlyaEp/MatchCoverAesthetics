# Match Cover Aesthetics
![License](https://img.shields.io/github/license/IlyaEp/MatchCoverAesthetics?style=for-the-badge)

> :man_student::woman_student: project for DevDays 2021 at [ITMO JB MSE](https://mse.itmo.ru/)

This repo contains code for Telegram bot, which creates Spotify playlists according to the mood of the sent pictures.

# Usage

1. **Clone repo**
    ```
    git clone https://github.com/IlyaEp/MatchCoverAesthetics.git
    ```
   
2. **Install dependencies**

    Install required Python packages with [pip](https://pip.pypa.io/en/stable/):
    ```
    pip install -r requirements.txt
    ```
3. **Pass your tokens**
    
    Make sure to insert valid tokens in [`bot.py`](https://github.com/IlyaEp/MatchCoverAesthetics/blob/main/src/bot.py):
    * [`TOKEN`](https://github.com/IlyaEp/MatchCoverAesthetics/blob/main/src/bot.py#L11) - Telegram API token
    * [`bot_id`](https://github.com/IlyaEp/MatchCoverAesthetics/blob/main/src/bot.py#L22) - id of Spotify profile to post playlists from
    * [`client_id`](https://github.com/IlyaEp/MatchCoverAesthetics/blob/main/src/bot.py#L23) - id of Spotify developer app
    * [`client_secret`](https://github.com/IlyaEp/MatchCoverAesthetics/blob/main/src/bot.py#L24) - secret of Spotify developer app

4. **(optional) Add your data to [`data`](https://github.com/IlyaEp/MatchCoverAesthetics/tree/main/data) folder**

    For now we've provided the data we gathered and processed, but if you want, you may replace it with your own.  

5. **Launch bot**

    Run the following command:
    
    ```
    python src/bot.py
    ```
