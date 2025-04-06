import sys

sys.path.insert(1, "../dependencies")
sys.path.insert(2, "../constants")

"""
Schema of Metadata of Document
    user_id: str        → reference ownership
    document_id: str    → reference which document the chunk belongs to
    gcs_link: str       → reference which document on GCS this chunk would be found in
    gcs_path: str       → reference which document file path on GCS 
    filename: str       → reference the name of document
    uploaded_date: str  → logging date when document is uploaded
"""


from typing import List, Dict, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from chromadb import HttpClient
from langchain_core.documents import Document
from constants.credentials import OPENAI_API_KEY
from constants.credentials import (
    CHROMA_DB_ACCESS_CLIENT_ID,
    CHROMA_DB_ACCESS_SECRET
)
from constants.utils import (
    CHROMA_DB_URL
)
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

chroma_client = HttpClient(
        host=CHROMA_DB_URL,
        headers={
            "CF-Access-Client-Id": CHROMA_DB_ACCESS_CLIENT_ID,
            "CF-Access-Client-Secret": CHROMA_DB_ACCESS_SECRET
        }
    )



# ------------------------
#        Chunking
# ------------------------
def chunk_text(raw_text: str, metadata: dict) -> List[Document]:
    
    """
    Parameters
    ----------
    raw_text: str
        raw content of document
    metadata: dict
        metadata for the entire document
        
    Returns
    -------
    list[Document]
        document chunks from the file
    """
    
    chunks = text_splitter.split_text(raw_text)
    return [
        Document(page_content=chunk, metadata={**metadata, "chunk_index": i}) for i, chunk in enumerate(chunks)
    ]

# ------------------------
# Prepare Embedding Payload
# ------------------------
def prepare_chroma_payload(chunks: List[Document]):
    
    """
    Parameters
    ----------
    documents: list[Document]
        document chunks
    
    Returns
    -------
    texts: list[str]
        raw content from document chunks
    metadatas: list[dict]
        metadata from document chunks
    ids: list[str]
        id from document chunks
    vectors: list[list[float]]
        embeddings of document chunks
    """
    
    texts = [doc.page_content for doc in chunks]
    metadatas = [doc.metadata for doc in chunks]
    ids = [
        f"{meta['user_id']}_{meta['document_id']}_{meta['chunk_index']}"
        for meta in metadatas
    ]
    vectors = embeddings.embed_documents(texts)
    return texts, vectors, metadatas, ids

# ------------------------
# Process Entire Document → Push to Chroma
# ------------------------
def upload_document_to_chroma(content: str, metadata: Dict) -> List[Document]:
    """Process a document into chunks with metadata."""
    # Split text into chunks
    chunks = chunk_text(raw_text=content, metadata=metadata)
    
    # Generate ChromaDB data
    _texts, _vectors, _metadatas, _ids = prepare_chroma_payload(chunks=chunks)
    
    # Get ChromaDB Collection
    collection = chroma_client.get_or_create_collection(name="prod_user_doc") ## can be parameterized in the future
    
    # Add data to ChromaDB
    collection.add(
        ids=_ids,
        documents=_texts,
        embeddings=_vectors,
        metadatas=_metadatas
    )

    return _ids, _texts, _vectors, _metadatas

def get_docs_from_chroma(ids: list[str], conditions: dict) -> dict:
    
    """
    Simply Retrieve the Document Chunks by Ids
    
    Returns => dict
    """
    
    collection = chroma_client.get_collection(name="prod_user_doc")
    result = collection.get(
        ids=ids
    )
    return result
    
def query_docs_from_chroma(prompt: str, premise: dict) -> dict:
    
    """ 
    Query the Document Chunks with Embeddings of a Prompt
    
    Parameters => prompt: str
    
    Returns => dict (['ids', 'distances', 'embeddings', 'metadatas', 'documents', 'uris', 'data', 'included'])
    """
    
    # Prepare the collection
    collection = chroma_client.get_collection(name="prod_user_doc")
    
    # Create embeddings for prompt
    search_embedding = embeddings.embed_query(prompt)
    
    # Query with embeddings
    result = collection.query(
        query_embeddings=search_embedding,
        n_results=5, # Top 5 most relevant
        where=premise # Filtering
    )
    
    return result ## keys: ['ids', 'distances', 'embeddings', 'metadatas', 'documents', 'uris', 'data', 'included']
    

# def categorize_document(text: str) -> str:
#     """Categorize a document into diagnosis, next_steps, or research_papers."""
#     llm = ChatOpenAI(model="gpt-4", temperature=0, api_key=OPENAI_API_KEY)

#     prompt = f"""Analyze the following medical document and categorize it into one of these categories:
#     - diagnosis: Contains information about medical conditions, symptoms, or diagnoses
#     - next_steps: Contains treatment plans, recommendations, or follow-up instructions
#     - research_papers: Contains research findings, studies, or clinical trials
    
#     Document:
#     {text[:2000]}  # First 2000 chars for categorization
    
#     Respond with ONLY the category name, nothing else."""

#     response = llm.invoke(prompt)
#     return response.content.strip().lower()


# def store_document_embeddings(
#     documents: List[Document], user_id: str, document_id: str
# ):
#     """Store document embeddings in Firebase."""
#     db = get_firestore_client()

#     # Create vector store
#     vectorstore = FAISS.from_documents(documents, embeddings)

#     # Get vectors and metadata
#     vectors = vectorstore.docstore.docs
#     metadata = [doc.metadata for doc in documents]

#     # Store in Firebase
#     doc_ref = (
#         db.collection("document_embeddings")
#         .document(user_id)
#         .collection("files")
#         .document(document_id)
#     )
#     doc_ref.set(
#         {
#             "vectors": [vector.page_content for vector in vectors],
#             "metadata": metadata,
#             "document_id": document_id,
#             "user_id": user_id,
#             "created_at": datetime.now().isoformat(),
#         }
#     )


# def retrieve_relevant_chunks(
#     query: str, user_id: str, document_id: str, k: int = 3
# ) -> List[Document]:
#     """Retrieve relevant document chunks based on a query."""
#     db = get_firestore_client()

#     # Get document embeddings from Firebase
#     doc_ref = (
#         db.collection("document_embeddings")
#         .document(user_id)
#         .collection("files")
#         .document(document_id)
#     )
#     doc_data = doc_ref.get().to_dict()

#     if not doc_data:
#         return []

#     # Recreate vector store
#     documents = [
#         Document(page_content=content, metadata=meta)
#         for content, meta in zip(doc_data["vectors"], doc_data["metadata"])
#     ]
#     vectorstore = FAISS.from_documents(documents, embeddings)

#     # Search for relevant chunks
#     results = vectorstore.similarity_search(query, k=k)
#     return results


# def process_and_store_document(
#     text: str, user_id: str, document_id: str, metadata: Dict
# ):
#     """Process a document, categorize it, and store its embeddings."""
#     # Categorize document
#     category = categorize_document(text)

#     # Process into chunks
#     documents = process_document(text, {**metadata, "category": category})

#     # Store embeddings
#     store_document_embeddings(documents, user_id, document_id)

#     return {
#         "category": category,
#         "num_chunks": len(documents),
#         "document_id": document_id,
#     }
