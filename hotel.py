import os
from serpapi import GoogleSearch
from dotenv import load_dotenv

class SerpapiWrapper:
    def __init__(self):
        self.base_url = "https://serpapi.com/search?engine="
        self.api_key = os.getenv("SERPAPI_API_KEY")

    def SearchHotel(self,query,check_in,check_out):
        params = {
            "engine": "google_hotels",
            "q": query,
            "hl": "en",
            "gl": "jp",
            "check_in_date": check_in,
            "check_out_date": check_out,
            "api_key": self.api_key,
            "currency": "JPY",
            "adults": 1,
        }
        search = GoogleSearch(params)
        return search.get_dict()
    def SearchFlight(self,_departure_id,_arrival_id,_outbound_date,_return_date):
        params = {
            "engine": "google_flights",
            "hl": "en",
            "gl": "jp",
            "api_key": self.api_key,
            "currency": "JPY",
            "adults": 1,
            "departure_id": _departure_id,
            "arrival_id": _arrival_id,
            "outbound_date": _outbound_date,
            "return_date": _return_date
        }
        search = GoogleSearch(params)
        return search.get_dict()

if __name__ == "__main__":
    load_dotenv("key.env")
    serpapi = SerpapiWrapper()
    #result = serpapi.SearchHotel("Tokyo","2025-10-10","2025-10-11")
    result = serpapi.SearchFlight("Tokyo","HND","AUS","2025-10-10","2025-10-11")
    print(result)