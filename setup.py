"""
One-time setup script to download required models
Run this before first use: python setup.py
"""

import os
import sys
from pathlib import Path
from huggingface_hub import hf_hub_download
from sentence_transformers import SentenceTransformer

def create_directories():
    """Create necessary directories"""
    dirs = ['models', 'watched_folder', 'chroma_db']
    for d in dirs:
        Path(d).mkdir(exist_ok=True)
    print("✓ Directories created")

def download_llm():
    """Download Llama 3.2 3B Instruct model (Q4_K_M quantized)"""
    print("\n📥 Downloading Llama 3.2 3B model (~2GB)...")
    print("This may take 5-10 minutes depending on your connection\n")
    
    try:
        model_path = hf_hub_download(
            repo_id="lmstudio-community/Llama-3.2-3B-Instruct-GGUF",
            filename="Llama-3.2-3B-Instruct-Q4_K_M.gguf",
            local_dir="models",
            local_dir_use_symlinks=False
        )
        print(f"✓ LLM downloaded to: {model_path}")
        return True
    except Exception as e:
        print(f"❌ LLM download failed: {e}")
        print("\nManual download option:")
        print("1. Visit: https://huggingface.co/lmstudio-community/Llama-3.2-3B-Instruct-GGUF")
        print("2. Download: Llama-3.2-3B-Instruct-Q4_K_M.gguf")
        print("3. Place in: models/ folder")
        return False

def download_embeddings():
    """Download sentence embedding model"""
    print("\n📥 Downloading embedding model (~80MB)...")
    
    try:
        # This will auto-download and cache the model
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        print("✓ Embedding model downloaded")
        return True
    except Exception as e:
        print(f"❌ Embedding download failed: {e}")
        return False

def main():
    print("="*60)
    print("LOCAL DOCUMENT CHAT - SETUP")
    print("="*60)
    
    # Create folders
    create_directories()
    
    # Download models
    llm_ok = download_llm()
    embed_ok = download_embeddings()
    
    print("\n" + "="*60)
    if llm_ok and embed_ok:
        print("✅ SETUP COMPLETE!")
        print("\nNext steps:")
        print("1. Place documents in: watched_folder/")
        print("2. Run: python app.py")
    else:
        print("⚠️  SETUP INCOMPLETE")
        print("Please resolve the errors above and run setup.py again")
    print("="*60)

if __name__ == "__main__":
    main()