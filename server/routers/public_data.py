import sys

sys.path.insert(1, "../dependencies")
sys.path.insert(2, "../constants")

from fastapi import APIRouter, Depends, HTTPException
from dependencies.data_dependencies import (
    get_nlm_condition_list,
    get_condition_link
)


router = APIRouter()

@router.get("/data/nlm-conditions")
async def get_nlm_conditions():
    """Retrieve conditions from Processed Data by NLM.
    
    Returns
    -------
    list[str]
    """
    
    conditions = get_nlm_condition_list()
    
    if not conditions or conditions == []:
        print("❌ Error: No conditions found.")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving conditions"
        )
        
    return {"conditions": conditions}