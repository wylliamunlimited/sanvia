from typing import TypedDict, List, Dict


class AIBrain(TypedDict):
    thread_id: str ## thread id for the current conversation
    prompt_chain: List[Dict[str, str]] = [{
                "role": "system",
                "content": (
                    "You are a medical assistant, but not a licensed medical professional. "
                    "You will provide insights based on the information and any patient data you have gathered. "
                    "You will ask question about users' condition if you need more information for judgements. You always ask more questions if you need more information. "
                    "You will response in the format of suspected condition, next steps, and disclaimers that clarify you are not diagnosing."
                    # "You will not provide any explicit medical advice or diagnosis, but you can talk about the generic knowledge related to the prompt. " ## NEED FURTHER TUNING
                )
            }] ## list of prompt chain
    
    ## Data Extracted
    data_extraction_completed: bool = False
    
    ## Personal Data
    data: Dict[str, Dict] ## user data
    
    ## Safety Parameter 
    risk_level: int ## 1 to 10 risk level 
    
    ## Proceeding Parameter
    proceed: bool # true: proceed, false: seek for more information
    
    ## Latest Message Relevance
    relevance: float ## 0 to 1 relevance score for the latest message
    
    ## Knowledge Parameter
    knowledge: List[Dict] ## tavily search result [full list]
    shortterm_knowledge: List[Dict] ## tavily search result for the current message
    ## sample: 
    #     "results": [
    #     {
    #       "title": "Dysbiosis: What is It and How to Heal Your Microbiome",
    #       "url": "https://drjockers.com/dysbiosis/",
    #       "content": "Dysbiosis is a condition where the gut microbiome is out of balance. Learn the major causes and support strategies to heal dysbiosis.",
    #       "score": 0.8790744,
    #       "raw_content": null
    #     },
    #     {
    #       "title": "Dysbiosis: Causes, treatments, and more - Medical News Today",
    #       "url": "https://www.medicalnewstoday.com/articles/dysbiosis",
    #       "content": "Dysbiosis is when there is an issue with the diversity of someone's gut bacteria. Understand more about the causes and treatments for this condition.",
    #       "score": 0.85995835,
    #       "raw_content": null
    #     },
    #     {
    #       "title": "Dysbiosis: What Is It, Causes, and More | Osmosis",
    #       "url": "https://www.osmosis.org/answers/dysbiosis",
    #       "content": "Dysbiosis is commonly linked to impaired gut barrier function and immune-mediated inflammation, which is a result of an excessive immune response. Therefore, there has been a potential association between intestinal dysbiosis and certain conditions, including inflammatory bowel disease (IBD), diabetes mellitus, and colorectal cancer.",
    #       "score": 0.8127637,
    #       "raw_content": null
    #     },
    #     {
    #       "title": "Gut Dysbiosis: Symptoms, Causes, Treatment and More - Health",
    #       "url": "https://www.health.com/gut-dysbiosis-8601756",
    #       "content": "Gut dysbiosis is an imbalance of gut microorganisms—like bacteria, fungi, and protozoa—in your intestines. A balanced gut flora (microbiome) supports functions like digestion and immune response.",
    #       "score": 0.76321954,
    #       "raw_content": null
    #     },
    #     {
    #       "title": "Dysbiosis: Symptoms and How To Treat It - Verywell Health",
    #       "url": "https://www.verywellhealth.com/what-is-intestinal-dysbiosis-1945045",
    #       "content": "Intestinal dysbiosis is a condition where the gut flora is imbalanced. Learn how gut dysbiosis can play a role in a variety of health problems.",
    #       "score": 0.7253574,
    #       "raw_content": null
    #     }
    #   ]
    
    category_focus: str | None ## category focus for the current conversation, will be changed into a ENUM in future sprints || None: general information, no focus
    
