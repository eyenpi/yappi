from typing import Dict, Any, List


def trim_spotify_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """Trim Spotify API responses to essential fields."""
    if not response or "error" in response:
        return response

    if "tracks" in response:
        # Search results or track list
        tracks = response["tracks"]["items"] if "items" in response["tracks"] else []
        return {
            "tracks": [
                {
                    "id": track.get("id"),
                    "name": track.get("name"),
                    "artists": [
                        {"name": a.get("name")} for a in track.get("artists", [])
                    ],
                    "album": {"name": track.get("album", {}).get("name")},
                    "duration_ms": track.get("duration_ms"),
                }
                for track in tracks[:5]  # Limit to 5 tracks
            ]
        }

    if "artists" in response:
        # Artist search or related artists
        artists = response["artists"]["items"] if "items" in response["artists"] else []
        return {
            "artists": [
                {
                    "id": artist.get("id"),
                    "name": artist.get("name"),
                    "genres": artist.get("genres", [])[:3],  # Limit to 3 genres
                }
                for artist in artists[:5]  # Limit to 5 artists
            ]
        }

    if "albums" in response:
        # Album search or artist albums
        albums = response["albums"]["items"] if "items" in response["albums"] else []
        return {
            "albums": [
                {
                    "id": album.get("id"),
                    "name": album.get("name"),
                    "artists": [
                        {"name": a.get("name")} for a in album.get("artists", [])
                    ],
                    "release_date": album.get("release_date"),
                }
                for album in albums[:5]  # Limit to 5 albums
            ]
        }

    return response  # Return original response if no matching format


def trim_ticketmaster_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """Trim Ticketmaster API responses to essential fields."""
    if not response or "error" in response:
        return response

    if "_embedded" in response:
        embedded = response["_embedded"]

        if "events" in embedded:
            # Event search results
            events = embedded["events"][:5]  # Limit to 5 events
            return {
                "events": [
                    {
                        "id": event.get("id"),
                        "name": event.get("name"),
                        "dates": {
                            "start": event.get("dates", {}).get("start", {}),
                        },
                        "venue": _extract_venue(event),
                        "priceRanges": event.get("priceRanges", [])[
                            :1
                        ],  # Only first price range
                    }
                    for event in events
                ]
            }

        if "venues" in embedded:
            # Venue search results
            venues = embedded["venues"][:5]  # Limit to 5 venues
            return {
                "venues": [
                    {
                        "id": venue.get("id"),
                        "name": venue.get("name"),
                        "city": venue.get("city", {}).get("name"),
                        "state": venue.get("state", {}).get("name"),
                        "address": venue.get("address", {}).get("line1"),
                    }
                    for venue in venues
                ]
            }

    # Single event details
    if "id" in response and "name" in response:
        return {
            "id": response.get("id"),
            "name": response.get("name"),
            "dates": {
                "start": response.get("dates", {}).get("start", {}),
            },
            "venue": _extract_venue(response),
            "priceRanges": response.get("priceRanges", [])[:1],
        }

    return response


def _extract_venue(event: Dict[str, Any]) -> Dict[str, Any]:
    """Extract essential venue information from an event."""
    if "_embedded" in event and "venues" in event["_embedded"]:
        venue = event["_embedded"]["venues"][0]
        return {
            "name": venue.get("name"),
            "city": venue.get("city", {}).get("name"),
            "state": venue.get("state", {}).get("name"),
        }
    return {}
