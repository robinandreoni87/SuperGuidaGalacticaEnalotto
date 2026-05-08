# 🌌 SuperEnalotto Galactic Mapping & Analytics

An advanced, interactive statistical engine and visualization suite for SuperEnalotto lottery data (1997-2026).

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Version](https://img.shields.io/badge/Version-5.7--Extreme-purple.svg)
![Technology](https://img.shields.io/badge/Stack-Python%20%7C%20HTML5%20%7C%20Canvas%20%7C%20Chart.js-orange.svg)

---

## 🎯 Overview
An advanced, interactive statistical engine and visualization suite for SuperEnalotto lottery data (1997-2026). Developed by **robinandreoni87**.

### 🚀 Key Features
- **Lexicographical Mapping**: Visualizes every draw in a 622-million combination dictionary space.
- **Gaussian Nebula**: Projects draws based on their sum, revealing the "Normal Distribution" (Bell Curve) of the lottery.
- **Fusion Mode**: A synchronized 60s animation comparing the dictionary and statistical models.
- **Historical Evolution**: A draw-by-draw chronological playback from 1997 to the present day.
- **Extreme Simulation**: Capable of processing and rendering over **150,000** hypothetical combinations to simulate the future "coloring" of the probability space.
- **Interactive Analytics**: Real-time Hot/Cold numbers, delays, and frequency charts.

---

## 🛠 Project Structure
- `genera_dashboard.py`: The core orchestration engine (Parses data, calculates indices, generates the HTML dashboard).
- `massive_gauss_gen.py`: High-speed generator for massive probabilistic datasets.
- `dashboard_statistica.html`: The final standalone, mobile-responsive interactive dashboard.
- `data/`: Archive of raw extraction files (`estrazioniYYYY.txt`).
- `simulations/`: Exported Markdown files containing thousands of non-repeating hypothetical combinations.

---

## 💻 Installation & Usage
1. **Clone the repo**:
   ```bash
   git clone https://github.com/robinandreoni87/SuperGuidaGalacticaEnalotto.git
   ```
2. **Run the Dashboard**:
   Open `dashboard_statistica.html` in any modern web browser.
3. **Generate new data**:
   Run the Python scripts (located in `src/`) to analyze updated draw files or create new simulations:
   ```bash
   python src/genera_dashboard.py
   python src/massive_gauss_gen.py
   ```

---

## 📱 Mobile Ready
The dashboard is fully responsive, optimized for both high-end desktop workstations and smartphones. Explore the galaxy of numbers from anywhere.

---

## ⚖️ License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
**Developed with ❤️ for Statistical Research.**
