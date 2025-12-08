"""
Main application entry point
Combines RAG engine with GUI and file monitoring
"""

import sys
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rag_engine import RAGEngine
from gui import ChatGUI

class DocumentWatcher(FileSystemEventHandler):
    """Monitor watched_folder for new documents"""
    
    def __init__(self, callback):
        self.callback = callback
        self.last_trigger = 0
        self.debounce_seconds = 2  # Wait 2 seconds before re-indexing
    
    def on_created(self, event):
        if not event.is_directory:
            self._trigger_reindex()
    
    def on_modified(self, event):
        if not event.is_directory:
            self._trigger_reindex()
    
    def on_deleted(self, event):
        if not event.is_directory:
            self._trigger_reindex()
    
    def _trigger_reindex(self):
        """Debounced re-indexing trigger"""
        current_time = time.time()
        if current_time - self.last_trigger > self.debounce_seconds:
            self.last_trigger = current_time
            print("📁 Files changed, triggering re-index...")
            self.callback()

def main():
    print("="*60)
    print("LOCAL DOCUMENT CHAT")
    print("="*60)
    
    # Check if models exist
    model_path = Path("models/Llama-3.2-3B-Instruct-Q4_K_M.gguf")
    if not model_path.exists():
        print("\n❌ Error: Model not found!")
        print("\nPlease run setup first:")
        print("  python setup.py")
        print("\nThis will download the required models (~2GB)")
        sys.exit(1)
    
    try:
        # Initialize RAG engine
        print("\n🚀 Starting RAG engine...")
        engine = RAGEngine()
        
        # Index existing documents
        print("\n📑 Indexing documents in watched_folder/...")
        count = engine.index_documents()
        if count > 0:
            print(f"✓ Indexed {count} documents")
        else:
            print("⚠️  No documents found in watched_folder/")
            print("   Add PDF, DOCX, TXT, or XLSX files to get started")
        
        # Setup file watcher
        watched_folder = "watched_folder"
        event_handler = DocumentWatcher(lambda: engine.index_documents())
        observer = Observer()
        observer.schedule(event_handler, watched_folder, recursive=False)
        observer.start()
        print(f"👁️  Watching: {watched_folder}/")
        
        # Launch GUI
        print("\n💬 Launching chat interface...")
        gui = ChatGUI(
            rag_engine=engine,
            on_index_callback=lambda: engine.index_documents()
        )
        
        print("\n✅ Application ready!")
        print("="*60 + "\n")
        
        # Run GUI (blocking)
        gui.run()
        
        # Cleanup
        observer.stop()
        observer.join()
        
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check if models are downloaded: python setup.py")
        print("2. Ensure watched_folder/ exists")
        print("3. Check requirements.txt are installed")
        sys.exit(1)

if __name__ == "__main__":
    main()