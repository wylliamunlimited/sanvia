# Sanvia Primary Repository

![Sanvia](tmp-logo.png)


![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=white)
![OpenAI API](https://img.shields.io/badge/OpenAI_API-412991?style=for-the-badge&logo=openai&logoColor=white)
<!-- ![FHIR API](https://img.shields.io/badge/FHIR_API-FF4081?style=for-the-badge&logo=fhir&logoColor=white) -->
![WHOOP API](https://img.shields.io/badge/WHOOP_API-00BFFF?style=for-the-badge&logo=whoop&logoColor=white)
![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=for-the-badge&logo=firebase&logoColor=white)


---

# Mission
Sanvia aims at providing personalized search experiences when users are querying for online health knowledge information from the internet. 

--- 

# Running the Repository...
This repository requires frontend & backend to be ran separately. Here is the instruction to the running of the repository.

## Frontend
1. Navigate into the <code>client</code> directory
2. Run <code>npm i</code> to install all the packages necessary for the application
3. Run <code>npm run dev</code> for launching the application locally

## Backend
1. Navigate into the <code>server</code> directory
2. Run <code>pip install -r requirements</code> to install all the python packages required for the application
3. Pull up terminal and install <code>Poppler</code> according to [pdf2image guide](https://pdf2image.readthedocs.io/en/latest/installation.html)
4. Run <code>fastapi run main.py</code> for debugging run 

## Vector Database 
Note: we made a Chroma vector database that is hosted through Google Cloud Platform virtual machines. The details can be found in [Sanvia Chroma](https://www.github.com/wylliamunlimited/sanvia/vector-db/README.md)

---

# Features

## Chat
We offer our user the experience to ask questions and get contextualized answers. Therefore we utilize OpenAI's 4o model to generate semantic response. Our chat experience is also regulated by LangGraph, specifically designed to monitor response types, actionable items (getting data across other systems, etc.), and detect informational gap for confident conclusion. 

## Documents
Considering cases when users have paper documents, pictures, etc. that are not accessible from the data providers we have access to, we allow user to upload their documents to allow further contextualization over own health. 

### Document RAG
We account for users' struggles to filter which documents are relevant to their concerns and which are not. Therefore, we created a vector database to allow intelligent querying of documents using cosine similarity algorithm, which is commonly used when processing linguisitics and finding semantic similarity. This allows users to...
1. Avoid explicit, annoying referencing of documents in their queries ("looking at my ...filename..." => gone)
2. Reduce frustration from linking documents to concerns

## WHOOP Data Integration
For wearable users, we hope to make use of data collected by their devices to gain full concepts over their health. To make an example, we implemented WHOOP data integration. Users need to consent us to access their WHOOP data through the connect button in profile page. After that, Sanvia handles the heavy liftings to
* Decide when WHOOP data is useful for user queries
* Include WHOOP data as part of LLM reasoning

## De-identification
For health information, extra layer of privacy is needed for users to feel safe and confident while getting information they need. Therefore, we include a de-identification feature in the backend, where information, before sent to 3rd party software, would be anonymized through a prototype version of critical information recognizer. 