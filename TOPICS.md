# 📚 Topics & Technologies Used in AthleteIQ — Kenexai Athlete

This document explains **every major topic and technology** used in this project in simple, easy-to-understand terms.

---

## 1. 🏗️ Full-Stack Architecture (Client-Server Model)

**Used?** ✅ Yes — `backend/app.py` (Flask server) + `frontend/` (React app)

The project follows a **client-server architecture**, which means the app is split into two parts:

- **Frontend (Client):** What the user sees and interacts with — the buttons, charts, dashboards, etc. Built with **React**.
- **Backend (Server):** The brain behind the scenes — processes data, runs ML models, and sends results back. Built with **Flask (Python)**.

The frontend talks to the backend using **REST APIs** (like `/api/players`, `/api/chat`). Think of it like a restaurant: the frontend is the menu you order from, and the backend is the kitchen that prepares your food.

---

## 2. 🔄 ETL Pipeline (Extract, Transform, Load)

**Used?** ✅ Yes — `backend/etl_pipeline.py`

ETL stands for:

| Step | What it does | In this project |
|------|-------------|-----------------|
| **Extract** | Pull raw data from a source | Reads tables from `database.sqlite` (Player, Match, Team, etc.) |
| **Transform** | Clean and fix the data | Handles missing values, converts data types, removes outliers |
| **Load** | Store the clean data for analysis | Creates analytics-ready "Gold" tables like `fact_player_performance` |

**Why it matters:** Real-world data is messy. Some players might have missing heights, some ratings might be extreme. ETL cleans all this up so the ML models get good data.

---

## 3. 🏅 Medallion Architecture (Bronze → Silver → Gold)

**Used?** ✅ Yes — `backend/etl_pipeline.py`

This is a way to organize data in layers, like refining raw metal:

| Layer | Quality | Example |
|-------|---------|---------|
| 🟤 **Bronze** | Raw, unprocessed data straight from SQLite | `Player`, `Match`, `Team` tables as-is |
| ⚪ **Silver** | Cleaned data — fixed types, filled missing values, removed outliers | Dates converted, ages calculated, goals counted |
| 🟡 **Gold** | Business-ready, denormalized tables optimized for analytics | `fact_player_performance`, `fact_injury_risk`, `dim_team` |

Think of it like cooking: Bronze is raw ingredients, Silver is washed and prepped, Gold is the finished dish.

---

## 4. ⭐ Star Schema (Data Warehousing)

**Used?** ✅ Yes — `backend/etl_pipeline.py` (Gold layer tables)

The Gold layer uses a **star schema** design with two types of tables:

- **Dimension Tables** (`dim_`) — Describe entities (who/what):
  - `dim_player` — Player info (name, age, height, attributes)
  - `dim_team` — Team info (name, tactics)
  - `dim_league` — League info (name, country)

- **Fact Tables** (`fact_`) — Store measurable events/metrics:
  - `fact_match` — Match results, goals, seasons
  - `fact_player_performance` — Composite performance scores
  - `fact_injury_risk` — Wearable sensor and injury data

**Why star schema?** It makes queries fast and simple. Want to know "top players in the Premier League"? Just join `fact_player_performance` with `dim_league`.

---

## 5. 📊 EDA (Exploratory Data Analysis)

**Used?** ✅ Yes — `backend/etl_pipeline.py` → `get_eda_data()` + `frontend/src/pages/DataQuality.jsx`

EDA is the process of **looking at your data to find patterns** before doing any machine learning. In this project, EDA includes:

- **Rating Distribution** — How many players have each rating (histogram)
- **Age Distribution** — Spread of player ages
- **Preferred Foot** — Left vs. Right preference breakdown
- **Correlation Matrix** — Which stats are related (e.g., does high attack = high midfield?)
- **Summary Statistics** — Average rating, age, performance score

The DataQuality page on the frontend visualizes all of this with charts.

---

## 6. 📈 Data Quality & Outlier Detection (IQR Method)

**Used?** ✅ Yes — `backend/etl_pipeline.py` → `transform_silver()` and `compute_data_quality()`

### Data Quality Report
The system checks every table for:
- **Missing cells** — How complete is the data?
- **Duplicate rows** — Any repeated records?
- **Column-level quality** — Each column's completeness %, data type, and unique count

### Outlier Detection (IQR)
Outliers are extreme values that can break ML models. The system uses the **IQR (Interquartile Range)** method:

```
Q1 = 25th percentile (lower quarter)
Q3 = 75th percentile (upper quarter)
IQR = Q3 - Q1
Outlier if value < Q1 - 1.5×IQR  OR  value > Q3 + 1.5×IQR
```

Any value outside these bounds is **clipped** (capped) to keep the data reasonable.

---

## 7. 🤖 Machine Learning — Classification

**Used?** ✅ Yes — `backend/ml_models.py`

### a) Random Forest Classifier (Injury Risk Prediction)

**What it does:** Predicts whether a player is at **high or low risk of injury** (binary classification: 0 or 1).

**How it works (simple):**
- Imagine 100 decision trees, each asking questions like "Is fatigue > 6?" or "Has the player had > 3 injuries?"
- Each tree votes: "High Risk" or "Low Risk"
- The final answer = **majority vote** from all 100 trees

**Features used:** Heart rate, sprint distance, training load, fatigue index, sleep hours, previous injuries, etc.

**Model evaluation:** Uses **accuracy score** and **feature importance** (which factors matter most for injury prediction).

### b) Gradient Boosting Classifier (Match Outcome Prediction)

**What it does:** Predicts the result of a football match — **Home Win, Draw, or Away Win** (multi-class classification).

**How it works (simple):**
- Starts with a weak model, then adds new trees one at a time
- Each new tree focuses on **fixing the mistakes** of the previous ones
- Like a student who reviews wrong answers and gradually gets better

**Features used:** Team tactical attributes like build-up speed, passing style, defence pressure, chance creation.

---

## 8. 🔮 Machine Learning — Clustering (K-Means)

**Used?** ✅ Yes — `backend/ml_models.py` → `train_player_clustering()`

**What it does:** Groups 11,000+ players into **5 clusters** based on their playing style.

**How it works (simple):**
1. Pick 5 random center points
2. Assign each player to the nearest center
3. Move the center to the average of all players in that group
4. Repeat until groups are stable

**Result:** Players are labeled as:
- `Elite Attack Players`
- `Strong Midfield Players`
- `Developing Defense Players`
- etc.

**Preprocessing:** Uses **StandardScaler** to normalize features so that all attributes (rating 0-100, age 16-40) are on the same scale before clustering.

---

## 9. 📐 Feature Engineering

**Used?** ✅ Yes — `backend/etl_pipeline.py` → `load_gold()`

Feature engineering means **creating new, meaningful columns** from existing data. Examples in this project:

| New Feature | How it's created |
|-------------|-----------------|
| `attack_score` | Average of finishing, heading, volleys, shot power, long shots, positioning |
| `midfield_score` | Average of passing, ball control, dribbling, vision, crossing, curve |
| `defense_score` | Average of marking, standing tackle, sliding tackle, interceptions |
| `physical_score` | Average of acceleration, sprint speed, agility, stamina, strength |
| `performance_score` | Weighted combination: 35% rating + 15% potential + 15% attack + 15% midfield + 10% defense + 10% physical |
| `total_goals` | `home_team_goal + away_team_goal` |
| `goal_difference` | `home_team_goal - away_team_goal` |
| `result` | "Home Win" / "Draw" / "Away Win" based on goal difference |
| `age` | Calculated from birthday |

---

## 10. 🧠 NLP (Natural Language Processing)

**Used?** ✅ Yes — `backend/nlp_intent_engine.py`

NLP is how the AI understands **human language**. When you type "Tell me about Messi", the system needs to figure out:

1. **Intent** — What do you want? → `player_profile`
2. **Entity** — Who/what are you asking about? → `Messi`

### Intent Classification
The system uses **keyword matching with fuzzy scoring**:
- Exact match: `"injury"` → full score
- Fuzzy match: Uses `SequenceMatcher` (similar to spell-check) to handle typos
- **16 different intents** are recognized: `player_profile`, `injury_risk`, `compare`, `lineup`, `match_prediction`, `anomalies`, `coaching`, etc.

### Entity Extraction
- **Player names** from message text
- **Team names** from database matching
- **Numbers** (e.g., "top **10** players")
- **Formations** (e.g., "lineup in **4-3-3**")
- **Metrics** (e.g., "best by **attack**" → `attack_score`)
- **VS patterns** (e.g., "Messi **vs** Ronaldo")

---

## 11. 💬 GenAI Chat Agent (Conversational AI)

**Used?** ✅ Yes — `backend/genai_chat_agent.py`

This is the **AI chatbot** — a multi-turn conversational agent that acts as a sports analyst. It:

- **Understands** your question using NLP (intent + entities)
- **Resolves pronouns** — If you asked about Messi, then say "What about his injury?", it knows "his" = Messi
- **Dispatches** the question to the right handler (17 different handlers)
- **Generates** professional analyst-style responses with markdown formatting, tables, and emoji icons

### Key Capabilities:
| You type... | AI does... |
|-------------|-----------|
| "Tell me about Messi" | Full player analysis with radar chart |
| "Is he at risk of injury?" | Injury prediction with explanation |
| "Compare Messi vs Ronaldo" | Side-by-side comparison |
| "Recommend lineup for Barcelona" | AI-optimized starting XI |
| "Detect anomalies" | Isolation Forest anomaly scan |
| "Predict Barcelona vs Real Madrid" | Match outcome forecast |

---

## 12. 🧩 Conversation Context Management

**Used?** ✅ Yes — `backend/conversation_context.py`

This module gives the chatbot **memory** across multiple messages. It tracks:

- **Last player discussed** — So "What about his injury?" works
- **Last team discussed** — So "Show their lineup" works
- **Conversation history** — Stores up to 20 turns
- **Pronoun resolution** — Replaces "him", "his", "he", "that player", "this team" with actual names

Without this, every message would be treated as a brand new conversation.

---

## 13. 🚨 Anomaly Detection

**Used?** ✅ Yes — `backend/anomaly_detector.py`

Anomaly detection finds **unusual or suspicious patterns** in the data. This project uses **two methods**:

### a) Z-Score Method (Univariate)
- Calculates how many **standard deviations** a value is from the average
- If Z-score > 2.5 → it's an anomaly
- Example: A player with performance score of 95 when average is 65

### b) Isolation Forest (Multivariate)
- An ML algorithm that detects outliers by **isolating unusual data points**
- Works on **multiple features** at once (fatigue, training load, sleep, matches, recovery)
- Points that are easy to isolate = anomalies
- `contamination=0.1` means it expects ~10% of data to be anomalous

Anomalies are classified as: 🔴 **CRITICAL**, 🟠 **HIGH**, or 🟡 **MODERATE**.

---

## 14. 🔋 Fatigue Monitoring & Injury Prediction

**Used?** ✅ Yes — `backend/fatigue_monitor.py`

### Fatigue Monitoring
Tracks player tiredness using simulated wearable sensor data:
- ❤️ Heart rate (avg and max)
- 🏃 Sprint and total distance (km)
- 📊 Training load
- 😴 Sleep hours
- 📅 Matches in last 30 days

Classifies fatigue into 4 levels:

| Level | Fatigue Index | Action |
|-------|--------------|--------|
| 🟢 Low | < 4 | No action needed |
| 🟡 Moderate | 4 – 5.5 | Monitor closely |
| 🟠 High | 5.5 – 7 | Reduce training by 40% |
| 🔴 Critical | > 7 | Mandatory rest |

### Explainable Injury Prediction
Goes beyond just saying "High Risk" — it explains **why**:
- Each contributing factor (fatigue, training load, sleep, age, etc.) is rated as HIGH/MODERATE/LOW impact
- Provides specific recommendations and recovery protocols

---

## 15. ⚽ Lineup Optimizer

**Used?** ✅ Yes — `backend/lineup_optimizer.py`

An algorithm that recommends the **optimal starting 11** considering:

1. **Position classification** — Assigns players to GK/DEF/MID/FWD based on their skill scores
2. **Formation support** — Handles 5 formations (4-3-3, 4-4-2, 3-5-2, 4-2-3-1, 3-4-3)
3. **Availability scoring** — Penalizes injured/fatigued players:
   ```
   availability = performance × (1 - injury_risk × 0.3) × (1 - fatigue/10 × 0.2)
   ```
4. **Team chemistry** — Calculates team balance based on rating consistency
5. **Bench selection** — Picks the best 7 players not in the starting XI

---

## 16. 📊 Data Visualization (Recharts)

**Used?** ✅ Yes — `frontend/src/pages/*.jsx` + `backend/chart_generator.py`

The project uses **Recharts**, a React-based charting library, for interactive visualizations:
- **Radar charts** — Player skill comparison (attack, defense, midfield, physical)
- **Bar charts** — Top players, goals by season
- **Line charts** — Performance trends over time
- **Pie charts** — Squad composition, injury risk distribution
- **Tables** — Player leaderboards, head-to-head records

The backend's `chart_generator.py` prepares the chart data, and the React frontend renders it.

---

## 17. 🌐 REST API (Flask)

**Used?** ✅ Yes — `backend/app.py`

A **REST API** is a standard way for the frontend to communicate with the backend using HTTP requests. Key endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/players` | GET | List all players with pagination & search |
| `/api/players/<id>` | GET | Get single player details |
| `/api/teams` | GET | List all teams |
| `/api/ml-metrics` | GET | Get ML model performance |
| `/api/clusters` | GET | Get skill-based player clusters |
| `/api/predict-match` | GET | Predict match outcome |
| `/api/anomalies` | GET | Detect anomalies |
| `/api/chat` | POST | Send message to AI chatbot |
| `/dashboard/coach` | GET | Coach dashboard data |
| `/dashboard/scout` | GET | Scout dashboard data |
| `/dashboard/analyst` | GET | Analyst dashboard data |

**CORS** (Cross-Origin Resource Sharing) is enabled via `flask-cors` so the frontend (running on a different port) can talk to the backend.

---

## 18. ⚛️ React (Frontend Framework)

**Used?** ✅ Yes — `frontend/src/`

React is a JavaScript library for building user interfaces. Key React concepts used:

- **Components** — Each page is a component (`CoachDashboard`, `Players`, `AIChat`, etc.)
- **JSX** — HTML-like syntax inside JavaScript files (`.jsx`)
- **React Router** — Client-side routing (navigate between `/coach`, `/scout`, `/ai-chat` without page reload)
- **State management** — Using React hooks (`useState`, `useEffect`)
- **Props** — Passing data between components

The app has a modern **sidebar navigation** layout with 6 pages.

---

## 19. ⚡ Vite (Build Tool)

**Used?** ✅ Yes — `frontend/vite.config.js`, `frontend/package.json`

Vite is a **next-generation build tool** that makes development fast:
- ⚡ Instant server start (no bundling during development)
- 🔥 Hot Module Replacement (see changes instantly without refreshing)
- 📦 Optimized production builds

It replaces older tools like Webpack and is much faster.

---

## 20. 🗄️ SQLite (Database)

**Used?** ✅ Yes — `database.sqlite` (313 MB)

SQLite is a **lightweight, file-based database** — no server needed, the entire database is a single file. The project uses a real-world **European Soccer Database** containing:

- **11,060 players** with 30+ attributes each
- **25,979 matches** across multiple seasons
- **299 teams** from European leagues
- Player attributes, team attributes, league & country data

The backend reads this using Python's `sqlite3` module.

---

## 21. 🐳 Docker & Docker Compose (Containerization)

**Used?** ✅ Yes — `Dockerfile.backend`, `Dockerfile.frontend`, `docker-compose.yml`

Docker packages the app into **containers** — lightweight, portable environments that work the same everywhere.

| File | What it does |
|------|-------------|
| `Dockerfile.backend` | Builds a Python container with Flask, installs dependencies, runs `app.py` |
| `Dockerfile.frontend` | **Multi-stage build**: First builds React app with Node.js, then serves it with Nginx |
| `docker-compose.yml` | Orchestrates both containers together, sets up ports (backend: 5000, frontend: 3000) |

**Multi-stage build** (frontend) is a Docker optimization — the final image only contains the compiled HTML/CSS/JS, not the entire Node.js environment.

---

## 22. 🩺 Standard Scaling (Feature Normalization)

**Used?** ✅ Yes — `backend/ml_models.py` (used in all 3 ML models)

**StandardScaler** transforms features so they have **mean = 0** and **standard deviation = 1**:

```
scaled_value = (original - mean) / standard_deviation
```

**Why?** ML algorithms like K-Means and SVM are distance-based. If one feature ranges 0–100 and another 0–10, the first feature dominates. Scaling puts them on equal footing.

---

## 23. 🧪 Train-Test Split (Model Evaluation)

**Used?** ✅ Yes — `backend/ml_models.py`

Before training, data is split into:
- **80% Training set** — The model learns from this
- **20% Test set** — The model is evaluated on this (unseen data)

This prevents **overfitting** (memorizing the training data instead of learning patterns).

```python
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
```

---

## 24. 📡 Natural Language to Data Query

**Used?** ✅ Yes — `backend/data_query_engine.py`

This system converts **natural language questions into data lookups**, similar to a simple Text-to-SQL engine:

| User says... | System interprets as... |
|-------------|----------------------|
| "Top 5 players by speed" | Sort by `sprint_speed`, limit 5 |
| "Players from Barcelona" | Find all players who played for Barcelona |
| "How many matches?" | Count of all matches |
| "Average rating" | `AVG(overall_rating)` |
| "Messi vs Ronaldo history" | Head-to-head match records |

It uses **regex pattern matching** to identify the query type, then routes to the appropriate handler.

---

## 25. 🔄 Performance Trend Analysis

**Used?** ✅ Yes — `backend/performance_analyzer.py` + `backend/chart_generator.py`

Tracks how a player's rating changes **over time** using historical attribute data:

- **Improving players** — Rating going UP across observations
- **Declining players** — Rating going DOWN
- **Stable players** — No significant change

Useful for scouting (find rising stars) and coaching (identify players losing form).

---

## 26. 🧑‍🏫 AI-Powered Coaching Plans

**Used?** ✅ Yes — `backend/genai_chat_agent.py` → `_handle_coaching()`

The AI generates **personalized coaching plans** for each player based on:
- Their **strengths** (maintain current training)
- Their **weaknesses** (targeted drills and exercises)
- Their **physical condition** (conditioning programs)
- Their **injury risk** (prevention protocols)
- Their **fatigue level** (workload management)

Includes a full **weekly training schedule** with specific sessions for each day.

---

## 27. 🧬 Synthetic Data Generation

**Used?** ✅ Yes — `backend/etl_pipeline.py` → `_generate_injury_data()`

Since real wearable sensor data isn't available, the project **generates realistic synthetic data** for injury prediction:
- Heart rate, sprint distance, total distance
- Training load, fatigue index, sleep hours
- Match count, previous injuries, recovery time

The synthetic data is **correlated with real player attributes** (e.g., older players get higher fatigue, players with low stamina get higher training load). This makes the data realistic for ML training.

---

## 28. 🔗 Correlation Analysis

**Used?** ✅ Yes — `backend/etl_pipeline.py` → `get_eda_data()`

Measures how strongly two variables are **related**:
- Correlation = +1 → Perfect positive relationship
- Correlation = 0 → No relationship
- Correlation = -1 → Perfect negative relationship

The project computes a **correlation matrix** for: overall rating, potential, attack score, midfield score, defense score, physical score, performance score, and age.

---

## 29. 🌐 SPA (Single Page Application) with Client-Side Routing

**Used?** ✅ Yes — `frontend/src/App.jsx` (React Router)

The frontend is a **Single Page Application (SPA)** — the browser loads one HTML page, and React handles switching between different "pages" (routes) **without full page reloads**. Routes include:

- `/data-quality` — Data Quality & EDA page
- `/players` — Player Database
- `/coach` — Coach Dashboard
- `/scout` — Scout & Manager Dashboard
- `/analyst` — Match Analyst Dashboard
- `/ai-chat` — AI Coach Chat

The Nginx configuration in the Dockerfile has `try_files $uri /index.html` to support SPA routing in production.

---

## 30. 📐 Label Encoding

**Used?** ✅ Yes — `backend/ml_models.py` (Match prediction)

ML models can't read text like "Home Win" or "Draw". **LabelEncoder** converts text categories into numbers:

```
"Away Win" → 0
"Draw" → 1
"Home Win" → 2
```

After prediction, it **decodes** back to the original text for display.

---

## Summary Table

| # | Topic | Where |
|---|-------|-------|
| 1 | Full-Stack Architecture | Backend + Frontend |
| 2 | ETL Pipeline | `etl_pipeline.py` |
| 3 | Medallion Architecture | `etl_pipeline.py` |
| 4 | Star Schema | Gold layer tables |
| 5 | EDA | `etl_pipeline.py` + `DataQuality.jsx` |
| 6 | Data Quality & Outlier Detection | `etl_pipeline.py` |
| 7 | Random Forest & Gradient Boosting | `ml_models.py` |
| 8 | K-Means Clustering | `ml_models.py` |
| 9 | Feature Engineering | `etl_pipeline.py` |
| 10 | NLP (Intent + Entity Extraction) | `nlp_intent_engine.py` |
| 11 | GenAI Chat Agent | `genai_chat_agent.py` |
| 12 | Conversation Context | `conversation_context.py` |
| 13 | Anomaly Detection | `anomaly_detector.py` |
| 14 | Fatigue Monitoring | `fatigue_monitor.py` |
| 15 | Lineup Optimizer | `lineup_optimizer.py` |
| 16 | Data Visualization (Recharts) | Frontend pages |
| 17 | REST API (Flask) | `app.py` |
| 18 | React | `frontend/src/` |
| 19 | Vite | `vite.config.js` |
| 20 | SQLite Database | `database.sqlite` |
| 21 | Docker & Docker Compose | Dockerfiles |
| 22 | Standard Scaling | `ml_models.py` |
| 23 | Train-Test Split | `ml_models.py` |
| 24 | NL to Data Query | `data_query_engine.py` |
| 25 | Performance Trend Analysis | `performance_analyzer.py` |
| 26 | AI Coaching Plans | `genai_chat_agent.py` |
| 27 | Synthetic Data Generation | `etl_pipeline.py` |
| 28 | Correlation Analysis | `etl_pipeline.py` |
| 29 | SPA + Client-Side Routing | `App.jsx` (React Router) |
| 30 | Label Encoding | `ml_models.py` |

---

> **Total: 30 Topics** covered in this project, spanning Data Engineering, Machine Learning, AI/NLP, Full-Stack Development, and DevOps.
