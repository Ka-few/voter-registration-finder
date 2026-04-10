# IEBC Registration Assistant

An AI-powered conversational agent designed to help Kenyan citizens locate their nearest IEBC (Independent Electoral and Boundaries Commission) voter registration centers via WhatsApp and SMS.

## 🚀 Overview

The system consists of three main components:
1.  **IEBC Data Scraper**: Automates the collection of registration center data from the IEBC website and indexes it into a local vector store (ChromaDB) using Sentence-Transformer embeddings.
2.  **LangGraph AI Agent**: A conversational brain powered by Google Gemini (Flash 1.5/2.0) that handles user queries, maintains session history in Redis, and uses professional registration tools.
3.  **Node.js Messaging Gateway**: An Express.js server that acts as a webhook bridge between Africa's Talking (SMS), Twilio (WhatsApp), and the AI Agent.

## 🛠️ Tech Stack

- **Backend**: Python 3.12 (FastAPI, LangGraph, LangChain)
- **Gateway**: Node.js (Express, Twilio SDK, Africa's Talking SDK)
- **Database**: ChromaDB (Vector Store), Redis (Session Cache)
- **LLM**: Google Gemini 1.5 Flash
- **Infrastructure**: Ngrok (for local webhook testing)

## 📁 Project Structure

```text
voter-registration-finder/
├── .env                  # Configuration and API keys
├── agent/                # Python AI Agent (Port 8000)
│   ├── bot.py            # LangGraph logic
│   ├── main.py           # FastAPI service
│   ├── tools.py          # IEBC lookup tools
│   └── venv/             # Shared virtual environment
├── gateway/              # Node.js Webhook Server (Port 3000)
│   ├── index.js          # Webhook routing & Rate limiting
│   └── package.json
└── scraper/              # IEBC Scraper & Indexer
    ├── scraper.py        # Playwright scraper logic
    └── embeddings.py     # ChromaDB indexing logic
```

## ⚙️ Setup Instructions

### 1. Prerequisites
- Python 3.12+
- Node.js 20+
- Redis Server (`sudo apt install redis-server`)

### 2. Environment Configuration
Create a `.env` file in the root directory:
```env
GOOGLE_API_KEY=your_gemini_key
ANTHROPIC_API_KEY=your_anthropic_key  # Optional
OPENAI_API_KEY=your_openai_key        # Optional
AT_API_KEY=your_africastalking_key
AT_USERNAME=your_at_username
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
AGENT_PORT=8000
```

### 3. Initialize the Agent & Scraper
Inside the root folder:
```bash
# Activate the shared venv
source agent/venv/bin/activate

# Populate the local search database
cd scraper
python scraper.py

# Launch the AI Agent
cd ../agent
python main.py
```

### 4. Start the Messaging Gateway
In a new terminal:
```bash
cd gateway
npm install
npm start
```

### 5. Local Webhook Testing (Ngrok)
To receive messages from Twilio/Africa's Talking on your local machine:
```bash
ngrok http 3000
```
Then update your Twilio Sandbox "When a message comes in" URL to: `https://your-ngrok-url.ngrok-free.app/whatsapp/incoming`

## 💬 Usage Examples

- **WhatsApp**: Send "Hi, where can I register in Nairobi?"
- **SMS**: Send "Find center in Westlands"
- **Language**: The agent responds in both English and Swahili automatically.

## 🛡️ Guardrails & Safety
- **No Personal Info**: The agent is restricted from asking for or storing ID numbers.
- **Scoping**: Only electoral topics are discussed; non-electoral questions are politely declined.
- **Concise SMS**: Responses are optimized to stay within character limits where possible.
