import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime, timedelta
import time
from typing import List, Dict, Tuple, Optional
import logging
from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SpotifyConfig:
    """Configuration class for Spotify API credentials"""
    client_id: str
    client_secret: str
    redirect_uri: str
    scope: str = "user-follow-read playlist-modify-public"
    timeout: int = 20

@dataclass
class ReleaseInfo:
    artist: str
    track_name: str
    album_name: str
    release_date: str
    track_url: str

class SpotifyReleaseRadar:
    def __init__(self, config: SpotifyConfig):
        """Initialize with Spotify configuration"""
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=config.client_id,
                client_secret=config.client_secret,
                redirect_uri=config.redirect_uri,
                scope=config.scope
            ),
            requests_timeout=config.timeout
        )

    def get_followed_artists(self) -> List[Dict]:
        """Fetch all artists the user follows"""
        logger.info("Fetching followed artists...")
        artists = []
        results = self.sp.current_user_followed_artists(limit=50)

        if 'artists' not in results:
            logger.error("Unexpected API response format")
            return []

        artists.extend(results['artists']['items'])
        logger.info(f"Found {len(artists)} artists...")

        while results['artists']['next']:
            try:
                results = self.sp.next(results['artists'])
                artists.extend(results['artists']['items'])
                logger.info(f"Found {len(artists)} artists...")
            except Exception as e:
                logger.error(f"Error during pagination: {e}")
                break

        logger.info(f"Total artists followed: {len(artists)}")
        return artists

    def get_artist_albums(self, artist_id: str) -> List[Dict]:
        """Get all albums for an artist using pagination, bump limit if not all songs are shown"""
        albums = []
        results = self.sp.artist_albums(
            artist_id,
            album_type='album,single',
            limit=50
        )
        albums.extend(results['items'])

        while results['next']:
            results = self.sp.next(results)
            albums.extend(results['items'])

        return albums

    def get_album_tracks(self, album_id: str) -> List[Dict]:
        """Get all tracks from an album"""
        tracks = []
        results = self.sp.album_tracks(album_id)
        tracks.extend(results['items'])

        while results['next']:
            results = self.sp.next(results)
            tracks.extend(results['items'])

        return tracks

    def create_playlist_with_new_releases(
        self,
        days_threshold: int = 7
    ) -> Tuple[List[str], List[ReleaseInfo]]:
        """Create a playlist with new releases from followed artists"""
        date_threshold = datetime.now() - timedelta(days=days_threshold)
        track_ids = []
        release_info = []

        followed_artists = self.get_followed_artists()
        logger.info(f"Checking releases for {len(followed_artists)} followed artists...")
        logger.info("=" * 50)

        for i, artist in enumerate(followed_artists, 1):
            logger.info(f"\nChecking artist {i}/{len(followed_artists)}: {artist['name']}")
            new_releases_found = False

            albums = self.get_artist_albums(artist['id'])

            for album in albums:
                try:
                    release_date = datetime.strptime(album['release_date'], '%Y-%m-%d')
                    if release_date >= date_threshold:
                        if not new_releases_found:
                            logger.info(f"🎵 New release(s) found for {artist['name']}!")
                            new_releases_found = True

                        tracks = self.get_album_tracks(album['id'])
                        for track in tracks:
                            track_ids.append(track['id'])
                            release_info.append(ReleaseInfo(
                                artist=artist['name'],
                                track_name=track['name'],
                                album_name=album['name'],
                                release_date=album['release_date'],
                                track_url=track['external_urls']['spotify']
                            ))
                            logger.info(f"   → Found: {track['name']} ({album['name']})")
                except ValueError:
                    continue

            if not new_releases_found:
                logger.info("   No new releases found")

            time.sleep(0.1)  # Rate limiting

        return track_ids, release_info

    def create_and_populate_playlist(
        self,
        track_ids: List[str],
        days_threshold: int
    ) -> Optional[Dict]:
        """Create a new playlist and add tracks to it"""
        if not track_ids:
            logger.info("\nNo new releases found.")
            return None

        logger.info("\n" + "=" * 50)
        logger.info(f"Found {len(track_ids)} new tracks! Creating playlist...")

        playlist_name = f"New Releases {datetime.now().strftime('%Y-%m-%d')}"
        playlist_description = (
            f"New releases from followed artists in the past {days_threshold} days. "
            f"Generated on {datetime.now().strftime('%Y-%m-%d')}"
        )

        user_id = self.sp.current_user()['id']
        playlist = self.sp.user_playlist_create(
            user_id,
            playlist_name,
            public=True,
            description=playlist_description
        )

        # Add tracks in batches (Spotify's 100 track limit I believe)
        for i in range(0, len(track_ids), 100):
            self.sp.playlist_add_items(playlist['id'], track_ids[i:i+100])

        return playlist

def main():
    try:
        config = SpotifyConfig(
            client_id=os.getenv('SPOTIFY_CLIENT_ID'),
            client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
            redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI')
        )

        radar = SpotifyReleaseRadar(config)
        days_threshold = 7

        track_ids, release_info = radar.create_playlist_with_new_releases(days_threshold)
        playlist = radar.create_and_populate_playlist(track_ids, days_threshold)

        if playlist:
            logger.info("\n✨ Success! ✨")
            logger.info(f"Created playlist with {len(track_ids)} tracks!")
            logger.info(f"Playlist URL: {playlist['external_urls']['spotify']}")

            logger.info("\nTracks added:")
            logger.info("=" * 50)
            for release in release_info:
                logger.info(f"\nArtist: {release.artist}")
                logger.info(f"Track: {release.track_name}")
                logger.info(f"Album: {release.album_name}")
                logger.info(f"Release Date: {release.release_date}")
                logger.info(f"Track URL: {release.track_url}")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
