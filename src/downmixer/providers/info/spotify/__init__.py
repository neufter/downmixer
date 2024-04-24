from __future__ import annotations

import logging

import spotipy

from .library import SpotifySong, SpotifyPlaylist
from downmixer.providers import BaseInfoProvider
from .utils import check_valid, ResourceType

logger = logging.getLogger("downmixer").getChild(__name__)


def _get_all(func, limit=50, *args, **kwargs):
    counter = 0
    next_url = ""
    items = []

    while next_url is not None:
        results = func(*args, **kwargs, limit=limit, offset=limit * counter)
        next_url = results["next"]
        counter += 1
        items += results["items"]

    return items


class SpotifyInfoProvider(BaseInfoProvider):
    def __init__(self):
        super().__init__()
        # TODO: Manage auth properly
        self.client = spotipy.Spotify(
            auth_manager=spotipy.SpotifyOAuth(
                scope="user-library-read,user-follow-read,playlist-read-private"
            )
        )

        self.connected = True

    def check_valid_url(self, url: str, type_filter: list[ResourceType] = None) -> bool:
        return utils.check_valid(url, type_filter)

    def _saved_tracks(
        self, limit: int = 20, offset: int = 0, market: str | None = None
    ) -> list[SpotifySong]:
        """Helper function to get a list of SpotifySong objects instead of just a dict from the Spotify API."""
        results = self.client.current_user_saved_tracks(
            limit=limit, offset=offset, market=market
        )
        return SpotifySong.from_provider_list(results["items"])

    def _playlists(self, limit: int = 50, offset: int = 0) -> list[SpotifyPlaylist]:
        """Helper function to get a list of SpotifyPlaylist objects instead of just a dict from the Spotify API."""
        results = self.client.current_user_playlists(limit=limit, offset=offset)
        return SpotifyPlaylist.from_provider_list(results["items"])

    def _playlist_songs(self, playlist_id: SpotifyPlaylist | str) -> list[SpotifySong]:
        """Helper function to get a list of SpotifySong objects instead of just a dict from the Spotify API."""
        if type(playlist_id) == SpotifyPlaylist:
            url = playlist_id.url
        else:
            url = playlist_id

        results = self.client.playlist_items(limit=100, playlist_id=url)
        return SpotifySong.from_provider_list(results["items"])

    def get_song(self, track_id: str) -> SpotifySong:
        super().get_song(track_id)

        result = self.client.track(track_id)
        return SpotifySong.from_provider(result)

    def get_all_playlist_songs(self, playlist_id: str) -> list[SpotifySong]:
        super().get_all_playlist_songs(playlist_id)

        return self._playlist_songs(playlist_id)

    def get_all_user_playlists(self) -> list[SpotifyPlaylist]:
        super().get_all_user_playlists()

        results = _get_all(self._playlists)
        return SpotifyPlaylist.from_provider_list(results)

    def get_all_user_songs(self) -> list[SpotifySong]:
        super().get_all_user_songs()

        results = _get_all(self._saved_tracks, limit=50)
        return SpotifySong.from_provider_list(results)
