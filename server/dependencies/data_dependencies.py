import os
import json
from fastapi import HTTPException, status
from typing import Union

BASE_DIR = os.path.dirname(__file__)
CONDITIONS_FILE_PATH = os.path.abspath(os.path.join(BASE_DIR, "../data/consumer-conditions.json"))


def get_nlm_condition_list() -> list:
    """Load condition list from JSON file."""
    try:
        
        with open(CONDITIONS_FILE_PATH, "r") as file:
            condition_list = json.load(file)
        
        return list(condition_list.keys())
        
    except FileNotFoundError:
        print("❌ Error: consumer-conditions.json file not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consumer conditions file not found."
        )
        
def get_condition_link(condition: str) -> Union[str, None]:
    """Get the link for a specific condition."""
    try:
        with open(CONDITIONS_FILE_PATH, "r") as file:
            condition_list = json.load(file)
        
        if condition not in condition_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Condition not found."
            )
        
        return condition_list[condition]
        
    except FileNotFoundError:
        print("❌ Error: consumer-conditions.json file not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consumer conditions file not found."
        )