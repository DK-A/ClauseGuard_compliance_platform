#!/bin/bash
set -e

PROFILE=$1
if [ -z "$PROFILE" ]; then
    PROFILE="RPI5"
fi

echo "Downloading offline models for profile: $PROFILE"

# Download fine-tuned embedding models to active cache
if [ "$PROFILE" == "RPI4" ]; then
    echo "Downloading Sentence-Transformers all-MiniLM-L6-v2..."
    python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
    
    echo "Downloading Qwen 2.5 1.5B Q4_K_M GGUF..."
    curl -L -o models/GGUF/qwen2.5-1.5b-instruct-q4_k_m.gguf \
        https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf
        
    echo "Downloading Phi-3 Mini GGUF..."
    curl -L -o models/GGUF/Phi-3-mini-4k-instruct-q4.gguf \
        https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf
else
    # RPI5 or LAPTOP
    echo "Downloading Sentence-Transformers nlpaueb/legal-bert-base-uncased..."
    python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('nlpaueb/legal-bert-base-uncased')"
    
    echo "Downloading LLaMA 3.1 8B Q4_K_M GGUF..."
    curl -L -o models/GGUF/meta-llama-3.1-8b-instruct-q4_k_m.gguf \
        https://huggingface.co/QuantFactory/Meta-Llama-3.1-8B-Instruct-GGUF/resolve/main/Meta-Llama-3.1-8B-Instruct-GGUF-v2.q4_K_M.gguf
        
    echo "Downloading Qwen 2.5 3B GGUF..."
    curl -L -o models/GGUF/qwen2.5-3b-instruct-q4_k_m.gguf \
        https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf
fi

echo "All offline weights successfully downloaded."
