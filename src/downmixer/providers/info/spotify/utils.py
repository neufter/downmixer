from __future__ import annotations

import re

from downmixer.providers import ResourceType

resource_type_map = {
    ResourceType.SONG: "track",
    ResourceType.ALBUM: "album",
    ResourceType.PLAYLIST: "playlist",
    ResourceType.ARTIST: "artist",
}


def check_valid(value: str, type_filter: list[ResourceType] = None) -> bool:
    """Checks using a regex if a string is a valid Spotify ID, URI or URL.

    Args:
        value (str): Arbitrary string that will be checked.
        type_filter (list[ResourceType]): Which resource types are accepted. Default any type.

    Returns:
         bool: True if the string given through `value` is a valid Spotify ID, URI or URL **and** it matches **any**
         of the specified resource types. Otherwise, returns False.
    """
    if type_filter is None:
        type_filter = [e for e in ResourceType]

    for t in type_filter:
        regex = r"spotify.*" + resource_type_map[t] + r"(?::|\/)(\w{20,24})"
        if re.search(regex, value) is not None:
            return True

    return False
