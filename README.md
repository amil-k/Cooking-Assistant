# 🍳 AI Cooking Assistant

A conversational AI-powered cooking assistant built with Streamlit. Ask it for recipes, modify them on the fly, or ask general cooking questions — all in a clean, dark-themed chat UI.

---

## Features

- **Recipe generation** — ask for any dish and get a structured recipe with ingredients, steps, cooking time, and difficulty
- **Recipe modification** — follow up with constraints like "make it vegan" or "no garlic" and the recipe updates
- **General cooking Q&A** — ask anything about cooking techniques, substitutions, or tips
- **Session memory** — the assistant remembers the current dish and all your requests within a session
- **Sidebar history** — see your active dish and recent requests at a glance

---

## Project Structure

```
├── app.py              # Streamlit UI
├── main.py             # LLM calls, prompt builder, validation logic
├── pydanticLayer.py    # Pydantic models and recipe validation
├── .env                # API key (not committed)
└── requirements.txt    # Python dependencies
```

---

## Setup

### 1. Clone the repo

```bash
git clone <your-repo-url>
cd ai-cooking-assistant
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your API key

Create a `.env` file in the project root:

```env
API_KEY=your_openrouter_api_key_here
```

Get a free API key at [openrouter.ai](https://openrouter.ai).

### 4. Run the app

```bash
streamlit run app.py
```

---

## Requirements

```
streamlit
requests
pydantic
python-dotenv
```

---

## How It Works

1. **User input** is sent to `build_prompt()` in `main.py`, which includes the current dish, session constraints, and the last known recipe as context.
2. The prompt is sent to the LLM via the OpenRouter API (`main.py → call_llm()`).
3. The response is parsed — if JSON is detected, it's extracted and validated against the Pydantic `Recipe` schema (`pydanticLayer.py`). If it's plain text, it's returned as a conversational reply.
4. On validation failure, the LLM is retried up to 2 times with the error message included in the prompt.
5. The result is rendered in the Streamlit UI — recipes as styled cards, text as chat bubbles.

---

## Configuration

| Variable | Location | Description |
|---|---|---|
| `API_KEY` | `.env` | Your OpenRouter API key |
| `MODEL` | `main.py` | LLM model to use (default: `meta-llama/llama-3.1-70b-instruct`) |
| `max_retries` | `main.py` | Number of retry attempts on invalid JSON (default: `2`) |

To switch models, update the `MODEL` variable in `main.py`:

```python
MODEL = "meta-llama/llama-3.1-70b-instruct"  # recommended
# MODEL = "openai/gpt-4o-mini"               # alternative
```

> **Note:** Smaller models (e.g. `llama-3-8b-instruct`) may produce unreliable JSON. A 70B+ model is recommended for best results.

---

## CLI Mode

You can also run the assistant in the terminal without Streamlit:

```bash
python main.py
```

---

## License

MIT