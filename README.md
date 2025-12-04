# Spotify New Releases Playlist Creator
I got very frustrated with Spotify since they decided that a release radar should not actually contain all your followed artist's new releases, but instead be filled with suggestions and ads.
This solves this problem and creates a new playlist with all the recent releases of all your followed artists. The code is not pretty, but it works. I believe something similar has been done before, but most of those applications did not fully work for me. 

## Features
- Creates a playlist with new releases from your followed artists
- Configurable time range (default: last 7 days)
- Handles both albums and singles
- Creates either public or private playlists
- Shows progress and found tracks during execution

## Prerequisites
- Python 3.x
- A Spotify account
- Spotify Developer credentials (see Setup below)

## Setup

### 1. Spotify Developer Account

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click "Create App"
4. Fill in the app details:
   - App name: just enter any name you like
   - App description: optional
   - Redirect URI: `http://localhost:8888/callback`
5. Click "Save"
6. On your app's page, note down the following:
   - Client ID
   - Client Secret (click "Show Client Secret" to reveal it)

### 2. Environment Setup
[Poetry](https://python-poetry.org/) is used to manage dependencies. You can install it by: 
```
curl -sSL https://install.python-poetry.org | python3 -
```
Then just create a virtual environment and install dependencies:
```
poetry install
```

### 3. Spotify setup 
You have to authenticate using the client ID and secret from step 1. To do that, either create a .env file like below, or pass in the credentials via
```bash
spotify-radar \
  --days 7 \
  --client-id YOUR_SPOTIFY_CLIENT_ID \
  --client-secret YOUR_SPOTIFY_CLIENT_SECRET \
  --redirect-uri http://127.0.0.1:8888/callback
```
or export them as environment variables
```bash
export SPOTIFY_CLIENT_ID="YOUR_SPOTIFY_CLIENT_ID"
export SPOTIFY_CLIENT_SECRET="YOUR_SPOTIFY_CLIENT_SECRET"
export SPOTIFY_REDIRECT_URI="http://127.0.0.1:8888/callback"
```

Do not use "localhost", see [Spotify security changes](https://developer.spotify.com/blog/2025-02-12-increasing-the-security-requirements-for-integrating-with-spotify).
## Usage

Run the script with default settings (7 days, private playlist):
```bash
spotify-radar --days N
```

### Options
Show all available options:
```bash
python script.py --help
```

```bash
--days, -d : Look for releases in the past N days (default: 7)
--public : Make the playlist public (default: private)
--playlist-name : Custom name for the playlist (default: New Releases YYYY-MM-DD)
--delay : Delay between API calls in seconds (default: 0.1)
--client-id : Spotify Client ID (overrides environment variables or .env)
--client-secret : Spotify Client Secret (overrides environment variables or .env)
--redirect-uri : Spotify Redirect URI (overrides environment variables or .env)
--env-file : Path to a .env file containing Spotify credentials
```

## First Run
When you run the script for the first time:
1. It will open your default web browser
2. Ask you to log in to Spotify (if not already logged in)
3. Request permission to access your Spotify account
4. Redirect you to a "connection refused" page (this is normal!)
5. Copy the entire URL from your browser
6. Paste it back into the terminal when prompted

After the first run, the authentication token will be cached and you won't need to authenticate again unless the token expires.

## Troubleshooting

### Authentication Issues
- Make sure your Client ID and Client Secret are correct in the `.env` file
- Check that the redirect URI in your Spotify App settings matches exactly: `http://localhost:8888/callback`
- Try deleting the `.cache` file and running the script again

### Rate Limiting
If you encounter rate limiting issues:
- Increase the delay between API calls: `--delay 0.2` or higher
- Wait a few minutes before trying again

### No Releases Found
- Check that you're following the artists on Spotify
- Try increasing the number of days to look back: `--days 30`

### Playlist not created
Somtimes a restart of Spotify is needed in order to update the playlists. 

### Stuck on "Fetching followed artists..." or other fetching operations
Not sure what causes this, but loggin out of the Spotify Developer Web Console and loggin back in fixed this for me.
