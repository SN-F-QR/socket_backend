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

    def SearchHotel(self, query, check_in, check_out, min_price=None, max_price=None):
        if min_price == "None":
            min_price = None
        if max_price == "None":
            max_price = None
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
            "sort_by": 3,
            "min_price": min_price,
            "max_price": max_price,
        }
        search = GoogleSearch(params)

        data = json.loads(search.get_raw_json())
        link = self.GetHotelLink(data)
        combined_results = {"link": link, "hotels": self.GetHotelResult(data)}
        # return data['search_metadata']['prettify_html_file']
        formatted_output = {
            "type": "defined",
            "target": "hotel",
            "value": [combined_results],
        }
        # json_str = json.dumps(formatted_output)
        # send_message_once(json_str)
        return formatted_output

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
            "deep_search": True,
        }
        search = GoogleSearch(params)
        outbound_data = json.loads(search.get_raw_json())
        link = self.GetFlightLink(outbound_data)
        depature_token = outbound_data["best_flights"][0]["departure_token"]
        return_params = {
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
            "departure_token": depature_token,
        }
        return_search = GoogleSearch(return_params)
        return_data = json.loads(return_search.get_raw_json())
        refine_outbound_data = self.GetFlightResult(outbound_data)
        # print(refine_outbound_data)
        refine_return_data = self.GetFlightResult(return_data)
        # print(refine_return_data)
        combined_results = {
            "link": link,
            "outbound": refine_outbound_data,  # 去程结果
            "return": refine_return_data,  # 回程结果
        }

        formatted_output = {
            "type": "defined",
            "target": "flight",
            "value": [combined_results],
        }
        # json_str = json.dumps(formatted_output)
        return formatted_output

    def SearchRestaurant(self, query):
        finalquery = query + " restaurant"
        params = {
            "engine": "google_local",
            "google_domain": "google.com",
            "hl": "en",
            "gl": "jp",
            "api_key": self.api_key,
            "q": finalquery,
        }
        search = GoogleSearch(params)
        data = json.loads(search.get_raw_json())
        link = self.GetRestaurantLink(data)
        combined_results = {
            "link": link,
            "query": finalquery,
            "local_results": self.GetRestaurantResult(data),
        }

        ## TODO: Extract the restaurant information
        formatted_output = {
            "type": "defined",
            "target": "restaurant",
            "value": [combined_results],
        }
        # json_str = json.dumps(formatted_output)
        return formatted_output

    def GetHotelLink(self, data):
        return data["search_metadata"]["prettify_html_file"]

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

    def GetFlightLink(self, data):
        return data["search_metadata"]["google_flights_url"]

    def GetFlightResult(self, data):
        result = []
        # 获取 best_flights 和 other_flights 数组
        best_flights = data.get("best_flights", [])
        other_flights = data.get("other_flights", [])

        # 将 best_flights 和 other_flights 合并，优先使用 best_flights
        combined_flights = best_flights.copy()
        if len(combined_flights) < 1:
            combined_flights.extend(other_flights)

        # 只取前 3 个航班组合
        for flight_group in combined_flights[:1]:
            flights_list = flight_group.get("flights", [])
            if not flights_list:
                continue  # 如果没有航段则跳过

            # 第一个航段：提取始发机场信息及时间
            first_segment = flights_list[0]
            departure_airport = first_segment.get("departure_airport", {})
            departure_id = departure_airport.get("id", "")
            dep_time_str = departure_airport.get("time", "")
            departure_date, departure_time = "", ""
            if dep_time_str:
                parts = dep_time_str.split(" ")
                if len(parts) >= 2:
                    departure_date = parts[0]
                    departure_time = parts[1]

            # 最后一个航段：提取目的机场信息及时间
            last_segment = flights_list[-1]
            arrival_airport = last_segment.get("arrival_airport", {})
            arrival_id = arrival_airport.get("id", "")
            arr_time_str = arrival_airport.get("time", "")
            arrival_date, arrival_time = "", ""
            if arr_time_str:
                parts = arr_time_str.split(" ")
                if len(parts) >= 2:
                    arrival_date = parts[0]
                    arrival_time = parts[1]

            # 航班价格一般位于 flight_group 顶层
            price = flight_group.get("price", None)

            entry = {
                "departure_id": departure_id,
                "arrival_id": arrival_id,
                "departure_date": departure_date,
                "departure_time": departure_time,
                "arrival_date": arrival_date,
                "arrival_time": arrival_time,
                "price": price,
            }

            result.append(entry)
            # 如果已收集到 3 个，则退出循环
            if len(result) == 3:
                break

        return result

    def GetRestaurantLink(self, data):
        return data["search_metadata"]["google_local_url"]

    def GetRestaurantResult(self, data):
        result = []
        for local_result_item in data["local_results"][:3]:
            rating = local_result_item.get("rating", None)
            name = local_result_item.get("title", "")
            price = local_result_item.get("price", "?")
            type = local_result_item.get("type", "")

            entry = {"name": name, "rating": rating, "price": price, "type": type}
            result.append(entry)
        return result


if __name__ == "__main__":
    load_dotenv("key.env")
    serpapi = SerpapiWrapper()
    result = serpapi.SearchHotel("Tokyo", "2025-10-10", "2025-10-11")
    # with open("test.json", "r", encoding="utf-8") as file:
    #     data = json.load(file)
    # result = serpapi.SearchFlight("HND","AUS","2025-10-10","2025-10-11")
    # result = serpapi.SearchRestaurant("Shibuya")

    print(json.dumps(result))
