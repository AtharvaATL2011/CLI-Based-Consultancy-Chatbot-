# 🤖 CLI-Based Consultancy Chatbot

> A terminal-based AI consultancy chatbot that assists users with **Education**, **Healthcare**, and **Finance** queries using smart intent routing and conversational AI.

Built completely in **Python**, this project demonstrates how AI assistants can work efficiently inside the command line — without requiring a web interface.

---

## 🚀 Overview

The CLI-Based Consultancy Chatbot simulates a real consultancy assistant that understands user queries and routes them intelligently to the correct domain.

Instead of a generic chatbot, this system:

- ✅ Detects user intent
- ✅ Routes queries to specialized domains
- ✅ Maintains conversational memory
- ✅ Works fully inside the terminal

---

## 🧠 Key Features

| Feature | Description |
|---|---|
| 💻 CLI Interaction | Fully terminal-based, no web UI required |
| 🎯 Intent Routing | Classifies and routes queries to the right domain |
| 🎓 Education Support | Career guidance, course selection, academic advice |
| 🏥 Healthcare Assistance | General health information and guidance |
| 💰 Finance Guidance | Financial planning and query support |
| 🧾 Memory Storage | Conversation history saved via SQLite |
| ⚡ Lightweight | Fast execution with minimal dependencies |
| 🔧 Modular Design | Easily extensible architecture |

---

## 📂 Project Structure

```
CLI-Based-Consultancy-Chatbot/
│
├── chatbot/              # Core chatbot logic
├── prompts/              # Domain-specific prompt templates
├── tests/                # Testing modules
├── chatbot_memory.db     # Conversation memory database
├── main.py               # Entry point
├── .env.example          # Environment variables template
├── setup.py              # Installation configuration
├── requirements.txt      # Python dependencies
└── README.md
```

---

## ⚙️ Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/AtharvaATL2011/CLI-Based-Consultancy-Chatbot-.git
cd CLI-Based-Consultancy-Chatbot-
```

### 2️⃣ Create a Virtual Environment *(Recommended)*

```bash
python -m venv venv
```

**Activate:**

```bash
# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
# or
pip install .
```

### 4️⃣ Setup Environment Variables

```bash
cp .env.example .env
```

Open `.env` and add your API key:

```env
OPENAI_API_KEY=your_api_key_here
```

---

## ▶️ Usage

Run the chatbot:

```bash
python main.py
```

**Example interaction:**

```
You: I need career advice after class 12
Bot: [Education Consultant Response]

You: What are symptoms of iron deficiency?
Bot: [Healthcare Consultant Response]

You: How should I start investing as a student?
Bot: [Finance Consultant Response]
```

---

## 🧩 How It Works

```
User Input (CLI)
      ↓
Intent Detection
      ↓
Domain Router
   ┌──┴──┬──────┐
   ↓     ↓     ↓
 Edu  Health Finance
   └──┬──┴──────┘
      ↓
 AI Response
      ↓
Memory Storage (SQLite)
```

1. User enters a query in the CLI
2. Chatbot analyzes the intent
3. Query is routed to the appropriate domain module:
   - 🎓 **Education**
   - 🏥 **Healthcare**
   - 💰 **Finance**
4. Response is generated using domain-specific AI prompts
5. Conversation is stored in the memory database

---

## 🛠 Tech Stack

- **Python** — Core language
- **LLM / AI APIs** — Response generation
- **SQLite** — Conversation memory storage
- **Prompt Engineering** — Domain-specific AI behavior
- **CLI Interface** — Terminal-based interaction

---

## 📈 Future Improvements

- [ ] Voice-enabled CLI interaction
- [ ] Multi-language support
- [ ] Advanced RAG-based knowledge retrieval
- [ ] Web dashboard interface
- [ ] Custom consultancy domains

---

## 🧪 Testing

Run all tests:

```bash
pytest tests/
```

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a Pull Request

---

## 👨‍💻 Authors

**Atharva Goel** & **Aayushman Umrao**
*Student Developers • AI Enthusiasts • Builders*

---

## 💡 Inspiration

This project explores how AI consultancy systems can operate efficiently in lightweight environments like terminals — bringing intelligent assistants closer to everyday developer workflows.

---

> ⭐ If you found this project useful, consider **starring the repository** — it helps others discover it!
