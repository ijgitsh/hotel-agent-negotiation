# 🤖 AI-Powered Hotel Negotiation with Multi-Agent Collaboration

This project simulates a **multi-agent negotiation protocol** between a budget-conscious traveler (CustomerAgent) and a group of hotel agents (HotelAgent), each powered by a **large language model** (LLM) using [CrewAI](https://github.com/joaomdmoura/crewai) and [LangChain OpenAI](https://github.com/langchain-ai/langchain).

Inspired by childhood memories of real-world haggling, this demo recreates that same dynamic — but in code.

---

## 💡 Features

- 🤝 Multi-agent negotiation simulation
- 🧠 LLM-based negotiation logic for each hotel
- 📉 Dynamic price adaptation with profit margin thresholds
- 🗣️ Realistic agent-to-agent dialogue powered by LLMs
- 📝 Logging and detailed negotiation summary
- 🧪 CLI input for user-defined starting offer

---

## 🧠 How It Works

1. The **CustomerAgent** starts with an initial offer.
2. Each **HotelAgent** evaluates the offer based on:
   - Base price
   - Minimum profit margin
   - Retry and discount strategy
3. Agents respond by:
   - Accepting the offer
   - Countering with a better deal
   - Rejecting if the offer is too low
4. The CustomerAgent iterates through rounds to find the best deal.

---

## 🧰 Tech Stack

- Python 3.8+
- [CrewAI](https://github.com/joaomdmoura/crewai)
- [LangChain](https://github.com/langchain-ai/langchain)
- [langchain-openai](https://pypi.org/project/langchain-openai/)
- OpenAI LLMs (e.g., `gpt-3.5-turbo`)
- `.env` for storing your `OPENAI_API_KEY`

---

## 📦 Installation

```bash
git clone https://github.com/ijgitsh/hotel-agent-negotiation.git
cd hotel-agent-negotiation
pip install -r requirements.txt
```

Create a .env file and add your OpenAI API key:
```bash
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
```

## ▶️ Running the Simulation
```bash
python negotiation.py
```
You’ll be prompted to enter your initial offer. The agents will then begin the negotiation, round by round.


##  Project Structure

```bash
├── negotiation.py         # Main script
├── requirements.txt       # Dependencies
├── .env                   # API key storage (you create this)
└── negotiation_log.txt    # Auto-generated log file
```

## 🧠 Lessons Learned
- AI agents can simulate negotiation behavior remarkably well.

- LLM-powered agents can represent personalized strategies and tone.

- CrewAI makes multi-agent coordination surprisingly intuitive.


## 🚀 Future Ideas

- Use a formal Multi-Agent Control Protocol (MCP) for message exchange.

- Add a GUI or web front-end.

- Introduce buyer profiles and negotiation personalities.

- Simulate airline, ride-share, or freelance pricing negotiations.

## 🙏 Acknowledgments
Inspired by the way my mother used to negotiate in local markets — always comparing prices, always persuasive. This project is a tribute to that spirit.

