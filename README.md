
# 🔍 HireSense.AI — Multi-Agent AI Hiring Intelligence System Based On Public Reviews on Hiring Process 

HireSense.AI is an advanced **AI-powered Hiring Intelligence platform** that analyzes a candidate’s resume, compares it with **real hiring patterns**, **role expectations**, and **public candidate experiences**, and produces a **deep, human-readable hiring report**.

Unlike basic resume analyzers, HireSense gives a **true hiring reality check** using multi-agent reasoning, community insights, and real-world patterns.

---

# ⭐ Key Features

### 🔮 1. Multi-Agent Architecture
HireSense uses four coordinated LLM agents:

| Stage | Agent | Purpose |
|------|--------|---------|
| 1 | Role Reality Agent | Learns real expectations of the target role from public patterns |
| 2 | Resume Reality Agent | Extracts skills, signals, strengths, weaknesses from resume |
| 3 | Fit Engine Agent | Compares resume vs role (gaps, seniority, risks, match score) |
| 4 | Friendly Report Agent | Produces a human-style hiring guidance report |

---

### 📎 2. Resume PDF Parsing
- Upload PDF resumes  
- Extracts clean text  
- Auto-detects exact skills  
- Auto-fills the skills section  
- Supports manual overrides  

---

### 🌐 3. Public Hiring Pattern Intelligence
Insights come from public hiring experiences:

- Glassdoor  
- Indeed  
- Reddit  
- LeetCode Discuss  
- GFG Interview Experiences  
- Blind (public posts)  
- YouTube interview breakdowns  
- Tech interview blogs  

---

### 🧩 4. Interview Round-by-Round Breakdown
- Number of rounds  
- What each round tests  
- Difficulty level  
- Topics asked  
- Common questions  
- High-probability themes  
- Tips from real patterns  

---

### 📊 5. Human-Formatted Reality Sections
- Role Reality  
- Resume Reality  
- Fit Analysis  


---

### 🙌 6. Community Insight Support
Users can optionally share:
- Their interview experiences  
- Hiring insights  
- Trends seen in industry  

---

### 💰 7. Token Usage + Cost Estimator
Estimates:
- Input tokens  
- Output tokens  
- Approx cost per run  

---

# 🏗 Project Structure

Hiresense.AI/
│
├── app.py

├── agents/

│   ├── role_reality_agent.py

│   ├── resume_reality_agent.py

│   ├── fit_agent.py

│   ├── friendly_agent.py

│   ├── resume_parser_agent.py

│   └── openai_client.py

├── requirements.txt

└── README.md

---

# ⚙️ Installation & Setup

### 1️⃣ Install Requirements
pip install -r requirements.txt

### 2️⃣ Add API Keys (.env)
OPENAI_API_KEY=your_openai_key
SERPAPI_KEY=your_serpapi_key

### 3️⃣ Run App
streamlit run app.py

### 4️⃣ Open Browser
http://localhost:8501

---

# 🌍 Deployment (Streamlit Cloud)
Push repo → Add env vars → Deploy.

---

# 🧭 Roadmap
- Live SERP hiring data  
- Probability-based fit score  
- Auto-resume rewriting  
- Multi-company comparison  
- Fine-tuned hiring models  

---

# 🤝 Contributing
PRs, ideas, and interview insights welcome.

---

# 📜 License
MIT License.

---

# 🙏 Credits
Built using:
- OpenAI GPT-4.1  
- Streamlit  
- Python  
- Public hiring intelligence  
- Community reviewers  
