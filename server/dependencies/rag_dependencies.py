import sys

sys.path.insert(1, "../dependencies")
sys.path.insert(2, "../constants")

from typing import List, Dict, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from constants.credentials import OPENAI_API_KEY
from dependencies.firebase_dependencies import get_firestore_client
from datetime import datetime

# Initialize embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=OPENAI_API_KEY)

# Initialize text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    separators=["\n\n", "\n", " ", ""],
)


def process_document(text: str, metadata: Dict) -> List[Document]:
    """Process a document into chunks with metadata."""
    # Split text into chunks
    chunks = text_splitter.split_text(text)

    # Create documents with metadata
    documents = []
    for i, chunk in enumerate(chunks):
        doc = Document(
            page_content=chunk,
            metadata={**metadata, "chunk_index": i, "total_chunks": len(chunks)},
        )
        documents.append(doc)

    return documents


def categorize_document(text: str) -> str:
    """Categorize a document into diagnosis, next_steps, or research_papers."""
    llm = ChatOpenAI(model="gpt-4", temperature=0, api_key=OPENAI_API_KEY)

    prompt = f"""Analyze the following medical document and categorize it into one of these categories:
    - diagnosis: Contains information about medical conditions, symptoms, or diagnoses
    - next_steps: Contains treatment plans, recommendations, or follow-up instructions
    - research_papers: Contains research findings, studies, or clinical trials
    
    Document:
    {text[:2000]}  # First 2000 chars for categorization
    
    Respond with ONLY the category name, nothing else."""

    response = llm.invoke(prompt)
    return response.content.strip().lower()


def store_document_embeddings(
    documents: List[Document], user_id: str, document_id: str
):
    """Store document embeddings in Firebase."""
    db = get_firestore_client()

    # Create vector store
    vectorstore = FAISS.from_documents(documents, embeddings)

    # Get vectors and metadata
    vectors = vectorstore.docstore.docs
    metadata = [doc.metadata for doc in documents]

    # Store in Firebase
    doc_ref = (
        db.collection("document_embeddings")
        .document(user_id)
        .collection("files")
        .document(document_id)
    )
    doc_ref.set(
        {
            "vectors": [vector.page_content for vector in vectors],
            "metadata": metadata,
            "document_id": document_id,
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
        }
    )


def retrieve_relevant_chunks(
    query: str, user_id: str, document_id: str, k: int = 3
) -> List[Document]:
    """Retrieve relevant document chunks based on a query."""
    db = get_firestore_client()

    # Get document embeddings from Firebase
    doc_ref = (
        db.collection("document_embeddings")
        .document(user_id)
        .collection("files")
        .document(document_id)
    )
    doc_data = doc_ref.get().to_dict()

    if not doc_data:
        return []

    # Recreate vector store
    documents = [
        Document(page_content=content, metadata=meta)
        for content, meta in zip(doc_data["vectors"], doc_data["metadata"])
    ]
    vectorstore = FAISS.from_documents(documents, embeddings)

    # Search for relevant chunks
    results = vectorstore.similarity_search(query, k=k)
    return results


def process_and_store_document(
    text: str, user_id: str, document_id: str, metadata: Dict
):
    """Process a document, categorize it, and store its embeddings."""
    # Categorize document
    category = categorize_document(text)

    # Process into chunks
    documents = process_document(text, {**metadata, "category": category})

    # Store embeddings
    store_document_embeddings(documents, user_id, document_id)

    return {
        "category": category,
        "num_chunks": len(documents),
        "document_id": document_id,
    }
