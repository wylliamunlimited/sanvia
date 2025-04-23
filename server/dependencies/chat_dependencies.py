import sys

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, "../dependencies")
sys.path.insert(2, "../constants")

from datetime import datetime
import random
from typing import List, Tuple
import json

from dependencies.firebase_dependencies import (
    get_firebase_user_from_token,
    update_chat_entry,
    get_chat,
)
from constants.request_obj import (
    EncryptedPromptRequest,
)
from constants.langgraph_obj import (
    AIBrain,
    # ChatMessage
)
from dependencies.ai_dependencies import (
    get_llm,
    initializeGraph,
    trigger_response,
)

async def create_new_thread(
        user,
        message_thread : list = []
    ):
    
    """Create new thread

    Description
    -----------
    Create a new chat session
    
    Parameters
    ----------
    user
        user that the chat would be created based on
    message_thread
        fundamental chat to be addded, e.g. system prompt

    Returns
    -------
    Tuple
        thread_id
        _graph
        _state
    """
    
    thread_id = (user["uid"]
                + datetime.now().strftime("%Y%m%d%H%M%S")
                + str(random.randint(0, 1000))
                )
    
    ## UNFINISHED
    if len(message_thread) > 0:
        _graph, _state = await initializeGraph(user_id=user["uid"])
    else:
        _graph, _state = await initializeGraph(prompt_chain=message_thread, user_id=user["uid"])
    
    _state["thread_id"] = thread_id
    return thread_id, _graph, _state ## returning metadata for newly created thread

