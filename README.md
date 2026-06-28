
# 🌤️ MausamBot — AI Weather Agent
=======

>>>>>>> cee98c4966eead02c9e41bb4e78d1af4f0cc1169

An AI-powered weather agent built with Python and Groq LLM that understands natural language in Roman Urdu and English, and provides real-time weather data.

## ✨ Features

- 🤖 Natural language understanding (Roman Urdu + English)
- 🌍 Real-time weather for any city worldwide
- 📅 3-day weather forecast
- 🏙️ Compare weather of two cities
- 💬 Friendly conversation with practical advice
- 🔧 Tool calling / Function calling architecture

## 🛠️ Tech Stack

- **Python 3.9+**
- **Groq API** (LLama 3.3 70B) — AI brain
- **OpenWeatherMap API** — Real-time weather data
- **python-dotenv** — Environment variables

## 🚀 Setup

### 1. Clone the repo
```bash
git clone https://github.com/asad3212/weather-agent.git
cd weather-agent
```

### 2. Virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install packages
```bash
pip install groq requests python-dotenv
```

### 4. API Keys
- **Groq:** https://console.groq.com
- **OpenWeatherMap:** https://openweathermap.org/api

Create `.env` file:
GROQ_API_KEY=your_groq_key

OPENWEATHER_API_KEY=your_openweather_key

### 5. Run
```bash
python3 agent.py
```

## 💬 Example Usage
Tum: Lahore ka mausam batao

Tum: Lahore aur Karachi compare karo

Tum: Islamabad ka 3 din ka forecast batao

## 👨‍💻 Author

**Asad** — BS Software Engineering, University of Gujrat
