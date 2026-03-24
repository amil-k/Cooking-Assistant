import os
import json
import requests
from typing import List, Optional
from pydantic import BaseModel, ValidationError
from dotenv import load_dotenv

load_dotenv()

# =========================
# 🔹 Pydantic Models
# =========================

class Ingredient(BaseModel):
    name: str
    quantity: str
    substitute: Optional[str]


class Step(BaseModel):
    step_number: int
    instruction: str


class Recipe(BaseModel):
    dish_name: str
    ingredients: List[Ingredient]
    steps: List[Step]
    cooking_time: str
    difficulty: str


# =========================
# 🔹 Config
# =========================

API_KEY = os.getenv("API_KEY")

URL = "https://openrouter.ai/api/v1/chat/completions"

MODEL = "meta-llama/llama-3-8b-instruct"  # stable free model


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
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 800
        },
        timeout=30
    )

    if response.status_code != 200:
        raise Exception(f"LLM Error: {response.text}")

    data = response.json()
    return data["choices"][0]["message"]["content"]


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
# 🔹 JSON Extractor
# =========================

def extract_json(text):
    start = text.find("{")
    end = text.rfind("}") + 1
    return text[start:end]


# =========================
# 🔹 Output Formatter
# =========================

def print_recipe(recipe):
    print("\n🍳 Recipe")
    print("=========")

    print(f"\nDish: {recipe.dish_name}")
    print(f"Cooking Time: {recipe.cooking_time}")
    print(f"Difficulty: {recipe.difficulty}")

    print("\nIngredients:")
    for ing in recipe.ingredients:
        if ing.substitute:
            print(f"- {ing.name} ({ing.quantity}) [substitute: {ing.substitute}]")
        else:
            print(f"- {ing.name} ({ing.quantity})")

    print("\nSteps:")
    for step in recipe.steps:
        print(f"{step.step_number}. {step.instruction}")


# =========================
# 🔹 Validation (Only when JSON)
# =========================

def handle_output(output, state):
    output = output.strip()

    # If JSON → validate
    if output.startswith("{"):
        try:
            cleaned = extract_json(output)
            parsed = json.loads(cleaned)

            recipe = Recipe(**parsed)

            # Update state
            state["recipe"] = parsed
            state["dish"] = parsed["dish_name"]

            print_recipe(recipe)

        except (json.JSONDecodeError, ValidationError) as e:
            print("AI: Sorry, something went wrong with the recipe format.")

    else:
        # Normal chatbot response
        print("\nAI:", output)


# =========================
# 🔹 Chatbot Loop
# =========================

state = {
    "dish": None,
    "recipe": None,
    "constraints": []
}

print("\n" + "="*40)
print(" AI COOKING CHATBOT ")
print("="*40)
print("Ask anything about cooking 🍳")
print("Type 'exit' to quit\n")


while True:
    user_input = input("You: ").strip()

    if user_input.lower() in ["exit", "quit"]:
        print("AI: Goodbye 👋")
        break

    # Save conversation context
    state["constraints"].append(user_input)

    prompt = build_prompt(user_input, state)

    try:
        output = call_llm(prompt)
        handle_output(output, state)

    except Exception as e:
        print("AI: Something went wrong. Try again.")