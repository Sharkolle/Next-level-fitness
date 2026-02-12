<div align="center">

# 🎮 NEXT LEVEL FITNESS

### AI-Powered Fitness Coach with RPG Progression

*Turn every workout into an epic quest. Level up IRL.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()
[![Status](https://img.shields.io/badge/status-active-success.svg)]()

[✨ Features](#features) • [🚀 Quick Start](#quick-start) • [📸 Screenshots](#screenshots) • [🎯 Roadmap](#roadmap) • [💬 Community](#community)

</div>

---

## 🌟 What is Next Level Fitness?

**Your webcam becomes your personal trainer.** No gym membership. No expensive equipment. Just you, your camera, and an AI that tracks your every move.

Inspired by **Solo Leveling**, this app transforms boring workouts into an RPG adventure:
- ✅ **AI pose detection** validates your form in real-time
- ✅ **Gain XP** and level up from E-Rank Hunter to S-Rank
- ✅ **Voice coaching** motivates you through tough sets
- ✅ **Global leaderboards** let you compete anonymously
- ✅ **Quest system** gives you daily challenges
- ✅ **100% privacy-first** - works offline, data stays local

---

## 🎥 Demo

> **[📹 Watch Demo Video](YOUR_YOUTUBE_LINK)** *(Coming Soon)*

<div align="center">
  <img src="docs/screenshots/workout_session.png" width="45%" alt="Workout Session"/>
  <img src="docs/screenshots/hunter_card.png" width="45%" alt="Hunter Card"/>
</div>

---

## ✨ Features

### 🤖 AI-Powered Form Detection
- **MediaPipe Pose Estimation** tracks 33 body landmarks
- Automatic rep counting with 95%+ accuracy
- Real-time form validation to prevent injury
- Supports 10+ exercises (push-ups, squats, planks, burpees, etc.)

### 🎮 Gamification System
- **Level 1-50+** progression with exponential XP curves
- **Hunter Ranks**: E → D → C → B → A → S
- **11+ Achievements** to unlock
- **Stat Tracking**: Strength, Agility, Stamina
- **Daily Quests** for bonus XP
- **Streak System** rewards consistency

### 🏆 Social Features
- Global leaderboards (anonymous)
- Shareable "Hunter Cards" showcasing your stats
- Cloud sync across devices (optional)
- Privacy-first: No tracking, no ads, no BS

### 🎤 Voice Coaching
- Real-time encouragement during workouts
- Rep counting announcements
- Achievement celebration alerts
- Motivational phrases randomized for variety

### 📊 Progress Tracking
- Workout history with detailed stats
- Visual progress graphs
- Total reps, workouts, and XP earned
- Exercise-specific performance metrics

---

## 🚀 Quick Start

### Option 1: Download Executable (Easiest)

**Windows:**
```bash
# Download latest release
https://github.com/YourUsername/NextLevelFitness/releases/latest

# Run NextLevelFitness.exe
```

**macOS:**
```bash
# Download latest .app bundle
https://github.com/YourUsername/NextLevelFitness/releases/latest

# Open NextLevelFitness.app
```

### Option 2: Run from Source

**Requirements:**
- Python 3.8 or higher
- Webcam (built-in or USB)
- 4GB RAM minimum

**Installation:**
```bash
# 1. Clone the repository
git clone https://github.com/YourUsername/NextLevelFitness.git
cd NextLevelFitness

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Set up cloud sync
cp .env.example .env
# Edit .env with your Supabase credentials

# 4. Run the app
python Next_level.py
```

**First-Time Setup:**
1. Create your hunter profile
2. Grant camera permissions
3. Complete tutorial workout
4. Start leveling up!

---

## 📸 Screenshots

<details>
<summary>Click to expand</summary>

### Main Dashboard
![Dashboard](docs/screenshots/dashboard.png)

### Workout Session (Live Pose Detection)
![Workout](docs/screenshots/workout.png)

### Hunter Profile & Stats
![Profile](docs/screenshots/profile.png)

### Leaderboard
![Leaderboard](docs/screenshots/leaderboard.png)

### Generated Hunter Card
![Hunter Card](docs/screenshots/hunter_card.png)

</details>

---

## 🎯 Supported Exercises

### Upper Body 💪
- Push-ups
- Tricep Dips

### Core & Abs 🔥
- Sit-ups
- Planks
- Bicycle Crunches

### Lower Body 🦵
- Squats
- Lunges
- Wall Sits

### Cardio & Full Body ⚡
- Jumping Jacks
- Mountain Climbers
- Burpees

*More exercises coming soon! Submit requests via [Issues](https://github.com/YourUsername/NextLevelFitness/issues).*

---

## 🛠️ Tech Stack

**Frontend:**
- CustomTkinter (Modern UI)
- OpenCV (Camera handling)
- Pillow (Image processing)

**AI/ML:**
- MediaPipe Pose (Google)
- NumPy (Mathematical operations)

**Backend:**
- Supabase (Cloud database - optional)
- SQLite (Local storage)

**Audio:**
- gTTS (Google Text-to-Speech)
- Pygame (Audio playback)

**Utilities:**
- python-dotenv (Environment management)
- threading (Async operations)

---

## 📋 System Requirements

### Minimum:
- **OS**: Windows 10, macOS 10.14, or Linux (Ubuntu 20.04+)
- **Processor**: Dual-core 2.0 GHz
- **RAM**: 4 GB
- **Camera**: Any webcam (720p recommended)
- **Storage**: 500 MB free space

### Recommended:
- **OS**: Windows 11, macOS 12+, or Linux (Ubuntu 22.04+)
- **Processor**: Quad-core 2.5 GHz+
- **RAM**: 8 GB
- **GPU**: Integrated graphics or better
- **Camera**: 1080p webcam for best accuracy

---

## 🗺️ Roadmap

### ✅ Current Version (v1.0)
- [x] Core pose detection
- [x] 10+ exercises
- [x] Gamification system
- [x] Voice coaching
- [x] Cloud sync (optional)
- [x] Leaderboards

### 🚧 Coming Soon (v1.1)
- [ ] Mobile app (iOS/Android)
- [ ] Custom workout routines
- [ ] Workout planner/scheduler
- [ ] Exercise form tutorials
- [ ] Multi-language support
- [ ] Dark/Light theme toggle

### 🔮 Future Ideas (v2.0+)
- [ ] Multiplayer challenges
- [ ] Social features (friend system)
- [ ] Equipment-based exercises
- [ ] Nutrition tracking integration
- [ ] Wearable device sync
- [ ] AI-generated workout recommendations

**Want a feature?** [Open an issue](https://github.com/YourUsername/NextLevelFitness/issues/new) or vote on existing requests!

---

## 🤝 Contributing

Contributions are welcome! Whether you're fixing bugs, adding features, or improving docs - every bit helps.

### How to Contribute:

1. **Fork the repo**
2. **Create a feature branch**: `git checkout -b feature/AmazingFeature`
3. **Commit your changes**: `git commit -m 'Add AmazingFeature'`
4. **Push to the branch**: `git push origin feature/AmazingFeature`
5. **Open a Pull Request**

### Areas Where We Need Help:
- 🐛 Bug fixes and testing
- 🎨 UI/UX improvements
- 📝 Documentation
- 🌍 Translations
- 🏋️ New exercise algorithms
- 🎬 Demo videos and tutorials

---

## 🐛 Known Issues

- **macOS Camera Permissions**: First launch may require manual permission grant
- **Linux Audio**: Some distros need additional PulseAudio setup
- **Low-End PCs**: Model complexity auto-adjusts, but <4GB RAM may struggle

See [open issues](https://github.com/Sharkolle/NextLevelFitness/issues) for full list.

---

## 📚 Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [User Manual](docs/USER_GUIDE.md)
- [Developer Setup](docs/DEVELOPMENT.md)
- [FAQ](docs/FAQ.md)

---

## 🔒 Privacy & Security

**Your data is YOURS:**
- ✅ Camera data processed locally in real-time (never saved/uploaded)
- ✅ Cloud sync is 100% optional
- ✅ Leaderboards use anonymous usernames only
- ✅ No tracking, no analytics, no ads
- ✅ Open source - audit the code yourself

Read our [Privacy Policy](PRIVACY.md) and [Terms of Service](TERMS.md).

---

## 📜 License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) file for details.

**TL;DR:** You can use, modify, and distribute this software freely. Just keep the license notice.

---

## 💬 Community

- **Discord**: [Join our server](YOUR_DISCORD_LINK) *(coming soon)*
- **Twitter**: [@YourHandle](https://x.com/thenextleveling)
- **Reddit**: [r/NextLevelFitness](YOUR_REDDIT) *(coming soon)*
- **Email**: ahmadbg900@gmail.com

---

## 🙏 Acknowledgments

**Inspiration:**
- Solo Leveling (manhwa/anime) for the hunter rank concept
- Beat Saber for proving fitness games can be addictive

**Technologies:**
- [MediaPipe](https://google.github.io/mediapipe/) by Google
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) by Tom Schimansky
- [Supabase](https://supabase.com/) for backend infrastructure

**Special Thanks:**
- Every beta tester who gave feedback
- My cat for moral support during 3am coding sessions

---

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Sharkolle/NextLevelFitness&type=Date)](https://star-history.com/#Sharkolle/NextLevelFitness&Date)

---

## 📊 Stats

![GitHub stars](https://img.shields.io/github/stars/Sharkolle/NextLevelFitness?style=social)
![GitHub forks](https://img.shields.io/github/forks/Sharkolle/NextLevelFitness?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/Sharkolle/NextLevelFitness?style=social)

---

<div align="center">

### 💪 Built with ❤️ by a janitor who codes at night

**If this app helps you get fit, consider:**

*just star the repo - it means the world! ⭐*

---

**Made with 🔥 and late-night energy drinks**

[⬆ Back to Top](#-next-level-fitness)

</div>
