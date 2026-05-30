#!/bin/bash
set -e

echo "=== ClauseGuard Raspberry Pi 5 Unattended Setup ==="

# 1. Update system & install dependencies
sudo apt-get update
sudo apt-get install -y build-essential cmake git curl python3-pip python3-venv nodejs npm libomp-dev

# 2. Build llama.cpp with ARM NEON & CPU compiler flags for Cortex-A76
if [ ! -d "llama.cpp" ]; then
    echo "Cloning and building llama.cpp..."
    git clone https://github.com/ggerganov/llama.cpp.git
    cd llama.cpp
    mkdir build
    cd build
    # Compile with Raspberry Pi 5 ARMv8.2-a Cortex-A76 compiler optimization flags
    cmake -DCMAKE_BUILD_TYPE=Release \
          -DCMAKE_C_FLAGS="-march=armv8.2-a+crypto+fp16 -mtune=cortex-a76" \
          -DCMAKE_CXX_FLAGS="-march=armv8.2-a+crypto+fp16 -mtune=cortex-a76" ..
    make -j$(nproc)
    cd ../..
fi

# 3. Download Models weights via Hugging Face/Ollama cache
mkdir -p models/GGUF
chmod +x edge/install_models.sh
./edge/install_models.sh RPI5

# 4. Install backend dependencies
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 5. Build frontend
cd frontend
npm install
npm run build
cd ..

# 6. Configure Systemd Services
sudo cp edge/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload

# Enable and start services
sudo systemctl enable clauseguard-backend.service
sudo systemctl enable clauseguard-worker.service
sudo systemctl enable clauseguard-frontend.service

sudo systemctl start clauseguard-backend.service
sudo systemctl start clauseguard-worker.service
sudo systemctl start clauseguard-frontend.service

echo "=== Setup complete! ClauseGuard edge platform is running on port 8000 ==="
