import asyncio
import os
import json
from serpapi import GoogleSearch
from dotenv import load_dotenv

# import keyboard

# import sockettest
# from sockettest import send_message_once


class SerpapiWrapper:
    def __init__(self):
        self.base_url = "https://serpapi.com/search?engine="
        self.api_key = os.getenv("SERPAPI_API_KEY")

    def SearchHotel(self, query, check_in, check_out):
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

        data = json.loads(search.get_raw_json())
        # return data['search_metadata']['prettify_html_file']
        formatted_output = {"target": "hotel", "value": self.GetHotelResult(data)}
        json_str = json.dumps(formatted_output)
        # send_message_once(json_str)
        return json_str

    def SearchFlight(self, _departure_id, _arrival_id, _outbound_date, _return_date):
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
            "return_date": _return_date,
        }
        search = GoogleSearch(params)
        data = json.loads(search.get_raw_json())
        ## TODO: Extract the best flight information
        return json.dumps({"target": "flight", "value": data["best_flights"]})

    def SearchRestaurant(self, Location):
        params = {
            "engine": "google_local",
            "google_domain": "google.com",
            "hl": "en",
            "gl": "jp",
            "api_key": self.api_key,
            "q": "restaurant",
            "Location": Location,
        }
        search = GoogleSearch(params)
        data = json.loads(search.get_raw_json())
        ## TODO: Extract the restaurant information
        return json.dumps(
            {
                "target": "restaurant",
                "value": data["search_metadata"]["google_local_url"],
            }
        )

    def GetHotelResult(self, data):
        result = []

        # 遍历 properties 列表的前三个元素
        for property_item in data["properties"][:3]:
            # 提取指定字段，如果字段缺失则使用默认值
            name = property_item.get("name", "")
            check_in_time = property_item.get("check_in_time", "")
            check_out_time = property_item.get("check_out_time", "")
            overall_rating = property_item.get("overall_rating", None)

            # lowest_price 可能在 "rate_per_night" 下
            lowest_price = None
            if "rate_per_night" in property_item:
                lowest_price = property_item["rate_per_night"].get("lowest")

            # 获取前 4 张缩略图链接
            thumbnails = []
            if "images" in property_item:
                thumbnails = [
                    img.get("thumbnail") for img in property_item["images"][:4]
                ]

            entry = {
                "name": name,
                "check_in_time": check_in_time,
                "check_out_time": check_out_time,
                "lowest_price": lowest_price,
                "overall_rating": overall_rating,
                "thumbnails": thumbnails,
            }

            result.append(entry)
        return result


if __name__ == "__main__":
    load_dotenv("key.env")
    serpapi = SerpapiWrapper()
    result = serpapi.SearchHotel("Tokyo", "2025-10-10", "2025-10-11")

    # result = serpapi.SearchFlight("HND","AUS","2025-10-10","2025-10-11")
    # result = serpapi.SearchRestaurant("Tokyo")

    print(result)
