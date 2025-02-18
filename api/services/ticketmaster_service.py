import yaml
from pathlib import Path
import requests
from functools import wraps
from api.config.settings import settings
from typing_extensions import Annotated
from pydantic import Field
from typing import Dict, Any

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
    def _filter_response(response: Dict[Any, Any], fields: str) -> Dict[Any, Any]:
        """Filter response to include only specified fields."""
        if not fields:
            return response

        field_list = [f.strip() for f in fields.split(",")]
        result = {}

        def extract_fields(
            data: Dict[Any, Any], field_paths: list[str]
        ) -> Dict[Any, Any]:
            output = {}
            for path in field_paths:
                parts = path.split(".")
                current = data
                valid = True
                for part in parts[:-1]:
                    if part not in current:
                        valid = False
                        break
                    current = current[part]
                if valid and parts[-1] in current:
                    nested_path = parts[0]
                    if nested_path not in output:
                        output[nested_path] = {}
                    current_dict = output[nested_path]
                    for part in parts[1:-1]:
                        if part not in current_dict:
                            current_dict[part] = {}
                        current_dict = current_dict[part]
                    current_dict[parts[-1]] = current[parts[-1]]
            return output

        if "_embedded" in response:
            for key in response["_embedded"]:
                result[key] = [
                    extract_fields(item, field_list)
                    for item in response["_embedded"][key]
                ]
            result["page"] = response.get("page", {})

        return result

    @staticmethod
    @with_yaml_doc("search_ticketmaster_events")
    def search_ticketmaster_events(
        fields: Annotated[
            str,
            Field(
                description=TICKETMASTER_DOCS["search_ticketmaster_events"]["params"][
                    "fields"
                ]
            ),
        ] = None,
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
        response = TicketmasterService._make_request("events.json", params)
        return TicketmasterService._filter_response(response, fields)

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
        fields: Annotated[
            str,
            Field(
                description=TICKETMASTER_DOCS["search_ticketmaster_venues"]["params"][
                    "fields"
                ]
            ),
        ] = None,
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
        response = TicketmasterService._make_request("venues.json", params)
        return TicketmasterService._filter_response(response, fields)

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
