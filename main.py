import os
import json
import requests
from dotenv import load_dotenv
from pydanticLayer import Recipe, validate_recipe

load_dotenv()

API_KEY = os.getenv("API_KEY")
URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "meta-llama/llama-3.1-70b-instruct"  # upgraded for reliable JSON


# =========================
# 🔹 LLM Call
# =========================

def call_llm(prompt):
    response = requests.post(
        URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 800
        },
        timeout=30
    )

    if response.status_code != 200:
        raise Exception(f"LLM Error: {response.text}")

    return response.json()["choices"][0]["message"]["content"]


# =========================
# 🔹 Prompt Builder
# =========================

def build_prompt(user_input, state):
    return f"""
You are an intelligent cooking assistant.

Your job:
- Understand the user's request
- Decide how to respond

If user wants:
1. Recipe generation or modification → return STRICT JSON
2. Explanation or question → return plain text

IMPORTANT:
- JSON must follow schema exactly
- Do NOT mix JSON and text
- Keep responses concise

Schema:
{{
  "dish_name": string,
  "ingredients": [
    {{
      "name": string,
      "quantity": string,
      "substitute": string or null
    }}
  ],
  "steps": [
    {{
      "step_number": integer,
      "instruction": string
    }}
  ],
  "cooking_time": string,
  "difficulty": "easy" | "medium" | "hard"
}}

Current state:
Dish: {state["dish"]}
Constraints: {state["constraints"]}
Recipe: {state["recipe"]}

User input:
{user_input}
"""


# =========================
# 🔹 Output Helpers
# =========================

def clean_llm_output(raw_output: str) -> str:
    raw_output = raw_output.strip()
    if raw_output.startswith("```"):
        raw_output = raw_output.replace("```json", "").replace("```", "")
    return raw_output.strip()


def extract_json(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError("No JSON object found in output")
    return text[start:end]


def print_recipe(recipe: Recipe):
    print(f"\n🍽️  {recipe.dish_name}")
    print(f"⏱️  Cooking time: {recipe.cooking_time}  |  Difficulty: {recipe.difficulty}")
    print("\n📦 Ingredients:")
    for ing in recipe.ingredients:
        sub = f"  (sub: {ing.substitute})" if ing.substitute else ""
        print(f"  - {ing.quantity} {ing.name}{sub}")
    print("\n📋 Steps:")
    for step in recipe.steps:
        print(f"  {step.step_number}. {step.instruction}")
    print()


# =========================
# 🔹 Validation with Retry
# =========================

def get_valid_recipe(prompt, state, max_retries=2):
    current_prompt = prompt

    for attempt in range(max_retries + 1):
        print(f"\n Attempt {attempt + 1}")

        raw_output = call_llm(current_prompt)
        cleaned_output = clean_llm_output(raw_output)

        # Try to extract JSON even if model added surrounding text
        try:
            json_str = extract_json(cleaned_output)
        except ValueError:
            # No JSON found — treat as plain text response
            return cleaned_output

        recipe, error = validate_recipe(json_str)

        if recipe:
            print("✅✅✅ Valid recipe obtained")
            return recipe

        print("❌❌❌ Validation failed:")
        print(error)

        current_prompt = f"""
Your previous response was invalid.

Error:
{error}

Fix the JSON and return ONLY valid JSON. No extra text, no markdown fences.

{prompt}
"""

    return None


# =========================
# 🔹 Output Handler
# =========================

def handle_output(output, state):
    if output is None:
        print("AI: Sorry, I couldn't generate a valid response after multiple attempts.")
        return

    if isinstance(output, Recipe):
        state["recipe"] = output.dict()
        state["dish"] = output.dish_name
        print_recipe(output)
        return

    if isinstance(output, str):
        output = output.strip()
        if output.startswith("{"):
            try:
                cleaned = extract_json(output)
                recipe, error = validate_recipe(cleaned)
                if recipe:
                    state["recipe"] = recipe.dict()
                    state["dish"] = recipe.dish_name
                    print_recipe(recipe)
                else:
                    print(f"AI: Sorry, something went wrong with the recipe format.\n{error}")
            except ValueError as e:
                print(f"AI: Sorry, something went wrong. {e}")
        else:
            print("\nAI:", output)


# =========================
# 🔹 Chatbot Loop (CLI only)
# =========================

if __name__ == "__main__":
    state = {
        "dish": None,
        "recipe": None,
        "constraints": []
    }

    print("\n" + "=" * 40)
    print(" AI COOKING CHATBOT ")
    print("=" * 40)
    print("Ask anything about cooking 🍳")
    print("Type 'exit' to quit\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ["exit", "quit"]:
            print("AI: Goodbye 👋")
            break

        state["constraints"].append(user_input)

        prompt = build_prompt(user_input, state)
        output = get_valid_recipe(prompt, state)
        handle_output(output, state)