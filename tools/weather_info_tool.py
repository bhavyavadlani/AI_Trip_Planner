import os
from utils.weather_info import WeatherForecastTool
from langchain.tools import tool
from typing import List
from dotenv import load_dotenv
from langchain_tavily import TavilySearch

class WeatherInfoTool:
    def __init__(self):
        load_dotenv()
        # Look for both variations of OpenWeatherMap API key
        self.api_key = os.environ.get("OPENWEATHERMAP_API_KEY") or os.environ.get("OPENWEATHER_API_KEY")
        self.weather_service = WeatherForecastTool(self.api_key)
        self.weather_tool_list = self._setup_tools()
    
    def _setup_tools(self) -> List:
        """Setup all tools for the weather forecast tool"""
        @tool
        def get_current_weather(city: str) -> str:
            """Get current weather for a city"""
            try:
                weather_data = self.weather_service.get_current_weather(city)
                if weather_data and 'main' in weather_data:
                    temp = weather_data.get('main', {}).get('temp', 'N/A')
                    desc = weather_data.get('weather', [{}])[0].get('description', 'N/A')
                    if temp != 'N/A':
                        return f"Current weather in {city}: {temp}°C, {desc}"
            except Exception as e:
                print(f"OpenWeather current weather failed: {e}. Falling back to Tavily.")

            # Fallback to Tavily Search
            try:
                tavily_tool = TavilySearch(topic="general")
                search_res = tavily_tool.invoke({"query": f"current weather in {city}"})
                return f"Current weather in {city} (via Search): {search_res}"
            except Exception as e:
                return f"Could not fetch weather for {city} due to error: {e}"
        
        @tool
        def get_weather_forecast(city: str) -> str:
            """Get weather forecast for a city"""
            try:
                forecast_data = self.weather_service.get_forecast_weather(city)
                if forecast_data and 'list' in forecast_data:
                    forecast_summary = []
                    for i in range(len(forecast_data['list'])):
                        item = forecast_data['list'][i]
                        date = item['dt_txt'].split(' ')[0]
                        temp = item['main']['temp']
                        desc = item['weather'][0]['description']
                        forecast_summary.append(f"{date}: {temp}°C, {desc}")
                    return f"Weather forecast for {city}:\n" + "\n".join(forecast_summary)
            except Exception as e:
                print(f"OpenWeather forecast failed: {e}. Falling back to Tavily.")

            # Fallback to Tavily Search
            try:
                tavily_tool = TavilySearch(topic="general")
                search_res = tavily_tool.invoke({"query": f"weather forecast for {city} next few days"})
                return f"Weather forecast for {city} (via Search): {search_res}"
            except Exception as e:
                return f"Could not fetch weather forecast for {city} due to error: {e}"
    
        return [get_current_weather, get_weather_forecast]