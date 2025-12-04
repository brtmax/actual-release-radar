#!/usr/bin/env python3
import argparse
import logging
import os

from dotenv import load_dotenv

from spotify_radar.radar import SpotifyConfig, SpotifyReleaseRadar

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Generate a Spotify playlist with new releases from followed artists."
    )
    parser.add_argument(
        "--days",
        "-d",
        type=int,
        default=7,
        help="Look for releases in the past N days (default: 7)",
    )
    parser.add_argument(
        "--public",
        action="store_true",
        help="Create the playlist as public (default: private)",
    )
    parser.add_argument(
        "--env-file",
        type=str,
        default=None,
        help="Optional path to a .env file with Spotify credentials",
    )
    parser.add_argument("--client-id", type=str, help="Spotify Client ID")
    parser.add_argument("--client-secret", type=str, help="Spotify Client Secret")
    parser.add_argument("--redirect-uri", type=str, help="Spotify Redirect URI")
    args = parser.parse_args()

    # Load .env if specified or exists
    if args.env_file:
        load_dotenv(args.env_file)
    else:
        load_dotenv()  # automatically loads .env if present

    # Determine credentials: CLI flags > environment variables
    client_id = args.client_id or os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = args.client_secret or os.getenv("SPOTIFY_CLIENT_SECRET")
    redirect_uri = args.redirect_uri or os.getenv("SPOTIFY_REDIRECT_URI")

    # Validate credentials
    if not all([client_id, client_secret, redirect_uri]):
        logger.error(
            "Missing Spotify credentials. Provide them via CLI flags, environment variables, or a .env file."
        )
        return

    config = SpotifyConfig(
        client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri
    )

    radar = SpotifyReleaseRadar(config)

    # Fetch new releases
    track_ids, release_info = radar.create_playlist_with_new_releases(args.days)

    if not track_ids:
        logger.info("No new releases found. Exiting.")
        return

    # Create playlist
    playlist = radar.create_and_populate_playlist(track_ids, args.days)

    if playlist:
        logger.info(f"\nPlaylist created: {playlist['name']}")
        logger.info(f"URL: {playlist['external_urls']['spotify']}")


if __name__ == "__main__":
    main()
