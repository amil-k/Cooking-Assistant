import json
from pydantic import BaseModel, ValidationError
from typing import List, Optional


class Ingredient(BaseModel):
    name: str
    quantity: str
    substitute: Optional[str] = None

class Step(BaseModel):
    step_number: int
    instruction: str


class Recipe(BaseModel):
    dish_name: str
    ingredients: List[Ingredient]
    steps: List[Step]
    cooking_time: str
    difficulty: str


def validate_recipe(raw_output: str):
    try:
        data = json.loads(raw_output)
        recipe = Recipe(**data)
        return recipe, None

    except json.JSONDecodeError as e:
        return None, f"JSONDecodeError: {str(e)}"

    except ValidationError as e:
        return None, f"ValidationError: {str(e)}"
    

