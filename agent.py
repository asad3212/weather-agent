import os
import json
import requests
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

def get_weather(city):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": OPENWEATHER_API_KEY, "units": "metric"}
    response = requests.get(url, params=params, timeout=10)
    data = response.json()
    if response.status_code != 200:
        return {"error": data.get("message", "Weather nahi mila")}
    return {
        "city": data["name"],
        "temperature_c": data["main"]["temp"],
        "feels_like_c": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "condition": data["weather"][0]["description"],
        "wind_speed_kmh": round(data["wind"]["speed"] * 3.6, 1),
    }

tools = [{"type": "function", "function": {"name": "get_weather", "description": "Kisi bhi city ka real-time weather deta hai", "parameters": {"type": "object", "properties": {"city": {"type": "string", "description": "Shehar ka naam"}}, "required": ["city"]}}}]

SYSTEM_PROMPT = "Tum ek helpful weather assistant ho jo Roman Urdu aur English mix mein baat karte ho. Jab user weather poochhe to get_weather tool use karo. Friendly aur mukhtasir jawab do."

def chat_with_agent(user_message, history):
    history.append({"role": "user", "content": user_message})
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
        tools=tools, tool_choice="auto", max_tokens=1024,
    )
    message = response.choices[0].message
    if message.tool_calls:
        history.append({"role": "assistant", "content": None, "tool_calls": [{"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}} for tc in message.tool_calls]})
        for tc in message.tool_calls:
            args = json.loads(tc.function.arguments)
            city = args.get("city", "")
            print(f"\n   🔧 Live data le raha hai: {city}...")
            result = get_weather(city)
            history.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(result, ensure_ascii=False)})
        final = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
            max_tokens=1024,
        )
        reply = final.choices[0].message.content
        history.append({"role": "assistant", "content": reply})
        return reply
    reply = message.content
    history.append({"role": "assistant", "content": reply})
    return reply

def main():
    print("=" * 45)
    print("🌤️  Smart Weather Agent (Groq)")
    print("   'exit' likho band karne ke liye")
    print("=" * 45)
    history = []
    while True:
        user_input = input("\nTum: ").strip()
        if user_input.lower() in ("exit", "quit", "bye"):
            print("\nAgent: Allah Hafiz! 👋")
            break
        if not user_input:
            continue
        reply = chat_with_agent(user_input, history)
        print(f"\nAgent: {reply}")

if __name__ == "__main__":
    main()
    