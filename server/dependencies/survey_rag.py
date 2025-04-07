import sys

sys.path.insert(1, "../dependencies")
sys.path.insert(2, "../constants")

from typing import Dict, List, Optional
from langchain_openai import OpenAIEmbeddings
from constants.credentials import OPENAI_API_KEY
from dependencies.firebase_dependencies import get_firestore_client

def get_survey_context(survey_data: Dict) -> str:
    """Convert survey data into a structured text format for embedding."""
    return f"""Patient Profile:
                Age: {survey_data['Age']}
                Gender: {survey_data['Gender']}
                Sex: {survey_data['Sex']}
                Height: {survey_data['Height']} cm
                Weight: {survey_data['Weight']} kg"""


######## ######## ######## Pausing on the Survey RAG, focusing on Document First ######### ######### #########
# def store_survey_embeddings(user_id: str, survey_data: Dict):
#     """Store survey data embeddings in Firebase."""
#     db = get_firestore_client()

#     # Process survey data into text
#     survey_text = process_survey_data(survey_data)

#     # Create document with metadata
#     doc = Document(
#         page_content=survey_text,
#         metadata={
#             "type": "survey_data",
#             "user_id": user_id,
#             "created_at": datetime.now().isoformat(),
#             "age": survey_data["Age"],
#             "gender": survey_data["Gender"],
#             "sex": survey_data["Sex"],
#             "height": survey_data["Height"],
#             "weight": survey_data["Weight"],
#         },
#     )

#     # Create vector store
#     vectorstore = FAISS.from_documents([doc], embeddings)

#     # Get vectors and metadata
#     vectors = vectorstore.docstore.docs

#     # Store in Firebase
#     doc_ref = db.collection("survey_embeddings").document(user_id)
#     doc_ref.set(
#         {
#             "vectors": [vector.page_content for vector in vectors],
#             "metadata": doc.metadata,
#             "user_id": user_id,
#             "created_at": datetime.now().isoformat(),
#             "last_updated": datetime.now().isoformat(),
#         }
#     )


# def retrieve_survey_context(user_id: str) -> Optional[Document]:
#     """Retrieve survey data context for a user."""
#     db = get_firestore_client()

#     # Get survey embeddings from Firebase
#     doc_ref = db.collection("survey_embeddings").document(user_id)
#     doc_data = doc_ref.get().to_dict()

#     if not doc_data:
#         return None

#     # Recreate document
#     return Document(page_content=doc_data["vectors"][0], metadata=doc_data["metadata"])


def get_bmi_context(survey_data: Dict) -> str:
    """Calculate BMI and provide relevant context."""
    height_m = survey_data["Height"] / 100
    bmi = survey_data["Weight"] / (height_m * height_m)

    bmi_category = ""
    if bmi < 18.5:
        bmi_category = "underweight"
    elif 18.5 <= bmi < 25:
        bmi_category = "normal weight"
    elif 25 <= bmi < 30:
        bmi_category = "overweight"
    else:
        bmi_category = "obese"

    return f"""BMI Analysis:
                The patient's BMI is {bmi:.1f}, which falls into the {bmi_category} category.
                This information may be relevant for:
                - Assessing health risks
                - Determining appropriate treatment plans
                - Setting health goals
                - Monitoring progress"""
