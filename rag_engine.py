"""
RAG (Retrieval-Augmented Generation) Engine
Handles indexing and querying with local LLM
"""

import os
# Disable ChromaDB telemetry to suppress warnings
os.environ['ANONYMIZED_TELEMETRY'] = 'False'
from pathlib import Path
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import LlamaCpp
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from document_processor import DocumentProcessor

class RAGEngine:
    """Offline RAG system using local LLM"""
    
    def __init__(self, db_path: str = "chroma_db"):
        self.db_path = db_path
        self.processor = DocumentProcessor()
        
        # Initialize embedding model (runs on CPU)
        print("Loading embedding model...")
        self.embeddings = SentenceTransformerEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Initialize vector store
        self.vectorstore = Chroma(
            persist_directory=db_path,
            embedding_function=self.embeddings
        )
        
        # Initialize local LLM
        model_path = Path("models/Llama-3.2-3B-Instruct-Q4_K_M.gguf")
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model not found at {model_path}\n"
                "Run setup.py first to download the model"
            )
        
        print("Loading LLM (this may take 30-60 seconds)...")
        self.llm = LlamaCpp(
            model_path=str(model_path),
            n_ctx=2048,  # Context window
            n_threads=4,  # CPU threads (adjust based on your CPU)
            temperature=0.1,  # Lower = more deterministic, less creative
            max_tokens=256,  # Reduced from 512 to prevent repetition
            stop=["Question:", "\n\nQuestion:", "Context:", "\n\nContext:"],  # Stop sequences
            verbose=False
        )
        
        # Create RAG chain
        self._setup_chain()
        print("✓ RAG engine ready")
    
    def _setup_chain(self):
        """Setup the retrieval QA chain"""
        prompt_template = """You are a precise document assistant. Answer questions using ONLY the context below.

STRICT RULES:
1. Use ONLY information explicitly stated in the Context
2. If the Context lacks relevant information, respond: "I don't have information about that in the documents."
3. Do NOT mix information from different documents
4. Do NOT invent connections between unrelated pieces of information
5. Keep answers concise and factual
6. If listing items, use the EXACT format from the source

Context:
{context}

Question: {question}

Answer (use exact information from context):"""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_kwargs={"k": 3}  # Back to simple top-3 retrieval
            ),
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
    
    def index_documents(self) -> int:
        """
        Index all documents in watched folder
        Returns: number of documents indexed
        """
        docs = self.processor.get_all_documents()
        
        if not docs:
            return 0
        
        # Extract text from all documents
        all_texts = []
        all_metadata = []
        
        for doc in docs:
            result = self.processor.extract_text(doc)
            if result:
                # Split text into chunks
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,  # Increased from 500 to capture full lists
                    chunk_overlap=100  # Increased from 50 for better context
                )
                chunks = text_splitter.split_text(result['content'])
                
                for i, chunk in enumerate(chunks):
                    all_texts.append(chunk)
                    all_metadata.append({
                        'source': result['filename'],
                        'chunk': i,
                        'doc_id': result['filename']  # Add document identifier
                    })
        
        if all_texts:
            # Clear existing database
            try:
                self.vectorstore.delete_collection()
                self.vectorstore = Chroma(
                    persist_directory=self.db_path,
                    embedding_function=self.embeddings
                )
            except:
                pass
            
            # Add documents to vector store
            self.vectorstore.add_texts(
                texts=all_texts,
                metadatas=all_metadata
            )
            self.vectorstore.persist()
            
            # Recreate chain with new retriever
            self._setup_chain()
        
        return len(docs)
    
    def query(self, question: str) -> Dict[str, any]:
        """
        Query the indexed documents
        Returns: {'answer': str, 'sources': List[str]}
        """
        if self.vectorstore._collection.count() == 0:
            return {
                'answer': "No documents indexed yet. Please add documents to the watched_folder.",
                'sources': []
            }
        
        result = self.qa_chain.invoke({"query": question})
        
        # Extract unique source documents
        sources = []
        if 'source_documents' in result:
            seen = set()
            for doc in result['source_documents']:
                source = doc.metadata.get('source', 'Unknown')
                if source not in seen:
                    sources.append(source)
                    seen.add(source)
        
        return {
            'answer': result['result'],
            'sources': sources
        }

if __name__ == "__main__":
    # Test the RAG engine
    engine = RAGEngine()
    
    print("\nIndexing documents...")
    count = engine.index_documents()
    print(f"Indexed {count} documents")
    
    if count > 0:
        print("\nTesting query...")
        response = engine.query("What are the main topics?")
        print(f"Answer: {response['answer']}")
        print(f"Sources: {response['sources']}")