import yaml
from pathlib import Path
import requests
from functools import wraps
from api.config.settings import settings
from typing_extensions import Annotated
from pydantic import Field

# Load documentation from YAML
docs_path = Path(__file__).parent.parent / "docs" / "ticketmaster_docs.yaml"
with open(docs_path, "r") as f:
    TICKETMASTER_DOCS = yaml.safe_load(f)


def with_yaml_doc(method_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        wrapper.yaml_doc = TICKETMASTER_DOCS[method_name]["method_doc"]
        return wrapper

    return decorator


class TicketmasterService:
    @staticmethod
    def _make_request(endpoint: str, params: dict = None) -> dict:
        """Helper method to make requests to Ticketmaster API"""
        if params is None:
            params = {}
        params["apikey"] = settings.TICKETMASTER_API_KEY

        url = f"{settings.TICKETMASTER_API_BASE_URL}/{endpoint}"
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return {"error": f"Failed to fetch data from Ticketmaster: {endpoint}"}

    @staticmethod
    @with_yaml_doc("search_ticketmaster_events")
    def search_ticketmaster_events(
        keyword: Annotated[
            str,
            Field(
                description=TICKETMASTER_DOCS["search_ticketmaster_events"]["params"][
                    "keyword"
                ]
            ),
        ] = None,
        countryCode: str = None,
        city: str = None,
        stateCode: str = None,
        classificationName: str = None,
        startDateTime: str = None,
        endDateTime: str = None,
        size: int = 20,
    ) -> dict:
        params = {k: v for k, v in locals().items() if v is not None and k != "cls"}
        return TicketmasterService._make_request("events.json", params)

    @staticmethod
    @with_yaml_doc("get_ticketmaster_event_details")
    def get_ticketmaster_event_details(
        id: Annotated[
            str,
            Field(
                description=TICKETMASTER_DOCS["get_ticketmaster_event_details"][
                    "params"
                ]["id"]
            ),
        ]
    ) -> dict:
        return TicketmasterService._make_request(f"events/{id}.json")

    @staticmethod
    @with_yaml_doc("search_ticketmaster_venues")
    def search_ticketmaster_venues(
        keyword: Annotated[
            str,
            Field(
                description=TICKETMASTER_DOCS["search_ticketmaster_venues"]["params"][
                    "keyword"
                ]
            ),
        ] = None,
        countryCode: str = None,
        stateCode: str = None,
        size: int = 20,
    ) -> dict:
        params = {k: v for k, v in locals().items() if v is not None and k != "cls"}
        return TicketmasterService._make_request("venues.json", params)

    @staticmethod
    @with_yaml_doc("get_ticketmaster_venue_details")
    def get_ticketmaster_venue_details(
        id: Annotated[
            str,
            Field(
                description=TICKETMASTER_DOCS["get_ticketmaster_venue_details"][
                    "params"
                ]["id"]
            ),
        ]
    ) -> dict:
        return TicketmasterService._make_request(f"venues/{id}.json")
