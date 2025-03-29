import sys

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, "../dependencies")
sys.path.insert(2, "../constants")

from datetime import datetime
import random
from typing import List
import json

from dependencies.firebase_dependencies import (
    get_firebase_user_from_token,
    update_chat_entry,
    get_chat,
)
from constants.request_obj import (
    PromptRequest,
)
from constants.langgraph_obj import (
    AIBrain,
    ChatMessage
)
from dependencies.ai_dependencies import (
    get_llm,
    initializeGraph,
    trigger_response,
)

def create_new_thread(
        user,
        message_thread : List[ChatMessage] = []
    ) -> AIBrain:
    thread_id = (user["uid"]
                + datetime.now().strftime("%Y%m%d%H%M%S")
                + str(random.randint(0, 1000))
                )
    
    ## UNFINISHED
    # if len(message_thread)
    
    _graph, _state = initializeGraph()
    
    _state["thread_id"] = thread_id
    return _state


    
