# services/rag_pipeline.py

import requests
import asyncio
from io import BytesIO

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader, UnstructuredEmailLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

from services.llm_service import get_llm_response

class RAGPipeline:
    def __init__(self):
        # Initialize the embedding model. 'all-MiniLM-L6-v2' is a great, lightweight choice.
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=200
        )

    def _load_document_from_url(self, url: str) -> list:
        """
        Downloads a document from a URL, determines its file type,
        and loads it using the appropriate LangChain document loader.
        """
        try:
            # Determine file extension from the URL path. It handles URLs with query parameters.
            file_extension = "." + url.split('/')[-1].split('?')[0].split('.')[-1].lower()
            
            response = requests.get(url)
            response.raise_for_status()
            
            # Use BytesIO to handle the file in memory
            file_in_memory = BytesIO(response.content)

            # Create a temporary file path with the correct extension to help loaders
            temp_file_path = f"temp_document{file_extension}"
            with open(temp_file_path, "wb") as f:
                f.write(file_in_memory.getvalue())

            # Select the loader based on the file extension
            if file_extension == ".pdf":
                loader = PyPDFLoader(temp_file_path)
            elif file_extension == ".docx":
                loader = UnstructuredWordDocumentLoader(temp_file_path)
            elif file_extension == ".eml":
                loader = UnstructuredEmailLoader(temp_file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")

            print(f"Loading document with {loader.__class__.__name__}...")
            documents = loader.load()
            return documents

        except requests.exceptions.RequestException as e:
            print(f"Error downloading file from URL {url}: {e}")
            return []
        except Exception as e:
            print(f"An error occurred during document loading: {e}")
            return []

    def setup_pipeline(self, document_url: str):
        """
        Sets up the RAG pipeline by loading, splitting, and indexing the document.
        This function should be called only once per document.
        """
        print("Loading document...")
        docs = self._load_document_from_url(document_url)
        if not docs:
            raise ValueError("Failed to load document. Cannot proceed.")

        print("Splitting document into chunks...")
        chunks = self.text_splitter.split_documents(docs)
        
        print("Creating vector store with FAISS...")
        self.vector_store = FAISS.from_documents(chunks, self.embeddings)
        print("Pipeline setup complete.")

    async def _process_single_question(self, question: str) -> str:
        """
        Processes a single question against the loaded document.
        """
        if not self.vector_store:
            return "Error: Document not processed. Please set up the pipeline first."
        
        print(f"Searching for relevant context for question: '{question[:30]}...'")
        # Retrieve the top 4 most relevant document chunks
        retrieved_docs = self.vector_store.similarity_search(question, k=4)
        
        # Combine the content of the retrieved chunks into a single context string
        context = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])
        
        print(f"Generating answer for question: '{question[:30]}...'")
        answer = get_llm_response(context, question)
        return answer

    async def run_queries(self, questions: list[str]) -> list[str]:
        """
        Asynchronously runs multiple questions through the RAG pipeline.
        """
        # Create a list of tasks to be run concurrently
        tasks = [self._process_single_question(q) for q in questions]
        
        # Run all tasks in parallel and wait for them to complete
        answers = await asyncio.gather(*tasks)
        return answers