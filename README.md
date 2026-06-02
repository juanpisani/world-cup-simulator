# 🏆 2026 World Cup Simulator

A professional-grade, interactive tournament simulator built with Python and Streamlit. This application simulates the full 48-team 2026 World Cup format, from the initial 12-group stage all the way to the final trophy presentation.

## 🌟 Key Features

- **Official 2026 Seeding:** Includes the official 12 groups (A through L) with realistic FIFA rankings for all 48 participating nations.
- **Dynamic Group Standings:** Live-calculating tables that strictly follow FIFA tie-breaking rules:
  1. Total Points
  2. Goal Difference (GD)
  3. Goals Scored (GS)
- **Advanced Simulation Engine:** 
  - **Probabilistic Logic:** Match results are generated based on FIFA ranking gaps, ensuring stronger teams have a higher probability of winning while still allowing for upsets and draws.
  - **Auto-Simulate:** One-click simulation for the entire tournament or just the remaining unplayed matches.
- **Round of 32 Qualification:** Automatically extracts the top 2 teams from each group and the **8 best third-placed teams** across the tournament using official bracket mapping.
- **Interactive Knockout Bracket:**
  - Full propagation from R32 to the Final.
  - **Cascading Reset:** Changing an earlier result automatically clears and resets all dependent future matches, preventing "ghost teams" in the bracket.
- **Penalty Shootout System:** Conceptually accurate penalty logic for knockout draws, including manual score entry and standard football notation (e.g., `1 (4) : (3) 1`).
- **Responsive Web UI:** A clean, modern dashboard with organized tabs for groups and a sequential view for the knockout stage.

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- pip (Python package installer)

### Local Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/juanpisani/world-cup-simulator.git
   cd world-cup-simulator
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   streamlit run app.py
   ```
   The app will open automatically in your default browser at `http://localhost:8501`.

## 🛠️ Built With
- **[Streamlit](https://streamlit.io/):** For the interactive web interface and state management.
- **[Pandas](https://pandas.pydata.org/):** For data structure manipulation and standings calculations.
- **[Dataclasses](https://docs.python.org/3/library/dataclasses.html):** For clean, type-safe data modeling.

## 📖 How It Works
- **State Persistence:** The app uses `st.session_state` to ensure that your manual inputs and simulation results are preserved as you navigate through different groups and rounds.
- **Tie-Breaking in Knockouts:** If a knockout match ends in a draw, the UI prompts for penalty shootout scores. In "Auto-Simulate" mode, the engine uses a random non-tying generator to decide who advances.
- **The "Best 3rd" Logic:** Implements the complex FIFA rules for selecting and placing the top 8 third-placed teams into their specific bracket slots.

## 📄 License
This project is open-source and available under the MIT License.

---
*Created with ❤️ for football fans and data enthusiasts.*
