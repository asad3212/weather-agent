import os
import json
import requests
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

# ─── Tool 1: Current Weather ───
def get_weather(city: str) -> dict:
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"q": city, "appid": OPENWEATHER_API_KEY, "units": "metric"}
        r = requests.get(url, params=params, timeout=10)
        d = r.json()

        if r.status_code == 404:
            return {"error": f"'{city}' naam ka koi shehar nahi mila. Spelling check karo ya poora naam likho!"}
        if r.status_code == 401:
            return {"error": "API key mein masla hai — admin se contact karo."}
        if r.status_code == 429:
            return {"error": "Bohot zyada requests ho gayi hain, thodi der baad try karo."}
        if r.status_code != 200:
            return {"error": f"Weather data nahi mila ({city})."}

        return {
            "city": d["name"],
            "country": d["sys"]["country"],
            "temperature_c": round(d["main"]["temp"], 1),
            "feels_like_c": round(d["main"]["feels_like"], 1),
            "humidity": d["main"]["humidity"],
            "condition": d["weather"][0]["description"],
            "wind_speed_kmh": round(d["wind"]["speed"] * 3.6, 1),
            "visibility_km": round(d.get("visibility", 0) / 1000, 1),
            "pressure_hpa": d["main"]["pressure"],
        }
    except requests.exceptions.Timeout:
        return {"error": "Server slow respond kar raha hai, thodi der baad try karo."}
    except requests.exceptions.ConnectionError:
        return {"error": "Internet connection check karo — server tak nahi pahunch paaya."}
    except Exception as e:
        return {"error": "Kuch unexpected masla aa gaya, dobara try karo."}
# ─── Tool 2: 3-Day Forecast ───
def get_forecast(city: str) -> dict:
    try:
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {"q": city, "appid": OPENWEATHER_API_KEY, "units": "metric"}
        r = requests.get(url, params=params, timeout=10)
        d = r.json()

        if r.status_code == 404:
            return {"error": f"'{city}' naam ka koi shehar nahi mila."}
        if r.status_code != 200:
            return {"error": f"Forecast data nahi mila ({city})."}

        daily = []
        seen = set()
        for entry in d["list"]:
            date = entry["dt_txt"].split(" ")[0]
            time = entry["dt_txt"].split(" ")[1]
            if date not in seen and time == "12:00:00":
                daily.append({
                    "date": date,
                    "temp_c": round(entry["main"]["temp"], 1),
                    "feels_like_c": round(entry["main"]["feels_like"], 1),
                    "condition": entry["weather"][0]["description"],
                    "humidity": entry["main"]["humidity"],
                    "wind_kmh": round(entry["wind"]["speed"] * 3.6, 1),
                })
                seen.add(date)
            if len(daily) >= 3:
                break
        return {"city": d["city"]["name"], "forecast": daily}
    except requests.exceptions.Timeout:
        return {"error": "Server slow respond kar raha hai, thodi der baad try karo."}
    except requests.exceptions.ConnectionError:
        return {"error": "Internet connection check karo."}
    except Exception:
        return {"error": "Kuch masla aa gaya, dobara try karo."}
# ─── Tool 3: Compare Two Cities ───
def compare_cities(city1: str, city2: str) -> dict:
    w1 = get_weather(city1)
    w2 = get_weather(city2)
    if "error" in w1 or "error" in w2:
        return {"error": "Ek ya dono cities nahi milin!"}
    return {"city1": w1, "city2": w2}

# ─── Tool Definitions ───
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Kisi bhi city ka abhi ka live weather deta hai — temperature, humidity, wind, visibility sab",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "Shehar ka naam jaise Lahore, Karachi, London"}
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_forecast",
            "description": "Kisi city ka agle 3 din ka weather forecast deta hai",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "Shehar ka naam"}
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare_cities",
            "description": "Do cities ka weather compare karta hai",
            "parameters": {
                "type": "object",
                "properties": {
                    "city1": {"type": "string", "description": "Pehla shehar"},
                    "city2": {"type": "string", "description": "Doosra shehar"},
                },
                "required": ["city1", "city2"],
            },
        },
    },
]

SYSTEM_PROMPT = """Tum ek AI weather assistant ho jiska naam "MausamBot" hai.

Tumhari baatein karne ka andaaz:
- Roman Urdu aur English mix mein baat karo
- Emojis zaroor use karo
- Temperature sun ke practical advice bhi do:
  * 40C+ → "Bohot garmi hai, paani zyada piyo!"
  * Barish → "Chhata saath rakhna!"
  * Thand → "Garmi kapre pehno!"
- Har jawab mein ye cheezein mention karo:
  * Temperature aur feels like
  * Humidity
  * Wind speed
  * Visibility

ZAROORI RULES — in ko kabhi mat todna:

1. SCOPE RESTRICTION (sabse zaroori rule):
   - Tum SIRF 2 cheezon ka jawab doge: (a) greetings/salam (hi, hello, salam, kaise ho) (b) weather se related sawal
   - Agar user koi aur topic poochhe (jaise: homework, coding, jokes, politics, general knowledge, advice, kahani, etc.) to politely mana karo:
     "Main sirf mausam ke baare mein madad kar sakta hoon! 🌤️ Kisi city ka weather poochna chahoge?"
   - Kisi bhi halat mein weather ke alawa kisi topic pe detailed jawab mat do

2. SPELLING TOLERANCE:
   - Agar user city ka naam galat spell kare (jaise "lahor", "karachy", "islamabaad", "isb") to samajh jao kis city ki baat ho rahi hai
   - Common Pakistani cities ki galat spellings ko automatically sahi samjho: Lahore, Karachi, Islamabad, Rawalpindi, Faisalabad, Multan, Peshawar, Sialkot, Gujranwala, Quetta
   - International cities ke liye bhi reasonable spelling mistakes samjho (London, Dubai, New York, etc.)
   - Agar city bilkul samajh na aaye to politely poocho: "Konsa shehar? Sahi naam bata do please"

3. GREETING RULE — BOHOT ZAROORI:
   - Agar user "hi", "hello", "salam", "kaise ho", "theek hoon", ya koi bhi casual baat kare jisme city ka naam NA ho, to SIRF baat karo — koi tool mat chalao
   - Tool SIRF aur SIRF tab chalao jab user EXPLICITLY kisi city ka naam le (jaise "Lahore", "Karachi ka mausam", "Multan mein barish")
   - Agar city ka naam clearly nahi mila message mein, to KABHI bhi koi tool mat chalao
   - Pichle messages se bhi city guess mat karo — sirf current message dekho
   - Agar pata nahi konsi city, to poocho: "Konsa shehar? Naam bata do please 🏙️"

4. Kabhi bhi guess mat karo weather data — hamesha tool use karo"""

def run_tool(name, args):
    if name == "get_weather":
        return get_weather(args["city"])
    elif name == "get_forecast":
        return get_forecast(args["city"])
    elif name == "compare_cities":
        return compare_cities(args["city1"], args["city2"])
    return {"error": "Unknown tool"}

def chat_with_agent(user_message, history):
    history.append({"role": "user", "content": user_message})
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
        tools=tools,
        tool_choice="auto",
        max_tokens=1500,
    )
    message = response.choices[0].message
    while message.tool_calls:
        history.append({
            "role": "assistant",
            "content": None,
            "tool_calls": [{"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}} for tc in message.tool_calls]
        })
        for tc in message.tool_calls:
            args = json.loads(tc.function.arguments)
            print(f"\n   🔧 {tc.function.name} → {args}...")
            result = run_tool(tc.function.name, args)
            history.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(result, ensure_ascii=False)})
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
            tools=tools,
            tool_choice="auto",
            max_tokens=1500,
        )
        message = response.choices[0].message
    reply = message.content
    history.append({"role": "assistant", "content": reply})
    return reply

def main():
    print("=" * 50)
    print("🌤️  MausamBot — AI Weather Assistant")
    print("   Kuch bhi poochho: city, forecast, compare!")
    print("   'exit' likho band karne ke liye")
    print("=" * 50)
    history = []
    while True:
        user_input = input("\nTum: ").strip()
        if user_input.lower() in ("exit", "quit", "bye"):
            print("\nMausamBot: Allah Hafiz! Mausam acha rahe! 🌈")
            break
        if not user_input:
            continue
        reply = chat_with_agent(user_input, history)
        print(f"\nMausamBot: {reply}")

if __name__ == "__main__":
    main()
