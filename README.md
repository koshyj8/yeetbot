
# 🧠 Yeetbot

Yeetbot is a multipurpose, full-stack Discord bot engineered for flexibility, utility, and long-term scalability. Originally developed as a passion project during 2020–2022, it grew into a modular, API-rich system used by over 200 users — integrating backend technologies, real-time data, and user-focused features.

> Built with **Python**, **Flask**, **SQLite**, and **RESTful APIs**, Yeetbot isn’t just fun — it’s functional, extensible, and cleanly architected.

---

## 🚀 Features

### 🛠️ Core Utilities
- **Server Moderation**: Kick, ban, purge, mute, unmute — all protected with role checks and permission layers.
- **Persistent Storage**: Fully integrated SQL-based system tracking user stats, inventory, and configurations.
- **Dynamic User Profiles**: Auto-created on first interaction, updated per usage (eco, games, etc).

### 🎧 Media
- **Music Playback**: Join VC, play/pause/resume/stop music, queue system (YouTube integration via `youtube_dl` or similar).
  
### 🎲 Games & Fun
- **Slot Machine**, **Trivia**, **Tic Tac Toe**, and other interactive games
- Persistent leaderboards for competitive tracking

### 🌐 API Integrations
- **TMDB API** – Fetch movies, TV shows, ratings, and metadata
- **JokeAPI** – Pulls programming/general jokes for instant fun
- **OpenWeatherMap** – Accurate weather forecasts by city or coordinates
- **CoinGecko** – Real-time crypto price checks for top tokens
- **WolframAlpha** – Complex query support: calculations, definitions, science, history

### 📈 Economy System
- Buy/sell items, maintain a wallet, shop listings, item inventory
- Custom item management with owner-only shop controls
- Balance tracking, bet-based games, and purchase logs

---

## 🧩 Tech Stack

- **Python 3.10+**
- **discord.py** (async)
- **Flask** (REST API backend for web-facing endpoints)
- **SQLite / aiosqlite** for persistent data
- **REST APIs** (TMDB, JokeAPI, CoinGecko, WolframAlpha, OWM)

---

## 🧪 Example Commands

```sh
!help
!weather mumbai
!crypto btc
!movie interstellar
!wolfram integral of x^2
!joke
!buy 1 2
!slot 100
!inventory
```

---

## 🛠️ Developer Notes

Yeetbot was engineered to be:
- **Modular**: Every cog is independent and self-contained.
- **Clean**: Pep8-compliant, commented where necessary, and separation of logic.
- **Extendable**: Easy to hook in new APIs or cogs without disrupting core architecture.

Want to add a new feature? Just drop it into a new cog and register the commands.

---

## 🔒 Permissions

- Read/Send Messages
- Manage Messages (for moderation)
- Connect/Speak (for music)
- Embed Links
- Use Slash Commands (if upgraded to `discord-py-interactions` or `pycord`)

---

## 🤝 Contributions

This project was a solo development journey by [Koshy John Oommen](https://github.com/yourusername) as part of an exploration into systems engineering, real-time bots, and backend logic.

If you're curious or want to fork it, feel free. Just drop a star if you liked the design.

---

## 📜 License

MIT License. Free to use, modify, and build upon.
