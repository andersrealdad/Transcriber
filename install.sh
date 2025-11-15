#!/bin/bash

###############################################################################
# Complete Installation Script
# Installs all system dependencies and sets up the project
###############################################################################

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║     AI-Powered Transcription & OCR System Installer            ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Check if running on Ubuntu/Debian
if ! command -v apt-get &> /dev/null; then
    echo -e "${RED}Error: This script requires apt-get (Ubuntu/Debian)${NC}"
    echo "For other systems, install packages manually:"
    echo "  - ffmpeg"
    echo "  - tesseract-ocr + language packs"
    echo "  - poppler-utils"
    echo "  - python3-dev python3-venv"
    exit 1
fi

echo -e "${YELLOW}This will install:${NC}"
echo "  • System packages (ffmpeg, tesseract, poppler)"
echo "  • Python dependencies (Faster-Whisper, PyTorch, etc.)"
echo "  • AI denoising tools (Demucs, DeepFilterNet)"
echo "  • Ollama models (optional)"
echo ""

read -p "Continue with installation? (y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    exit 0
fi

echo ""
echo -e "${BLUE}[1/6] Installing system packages...${NC}"
echo ""

sudo apt-get update

# Required packages
PACKAGES=(
    "ffmpeg"
    "tesseract-ocr"
    "tesseract-ocr-eng"
    "tesseract-ocr-nor"
    "poppler-utils"
    "python3-dev"
    "python3-venv"
    "python3-pip"
)

for pkg in "${PACKAGES[@]}"; do
    if dpkg -l | grep -q "^ii  $pkg"; then
        echo -e "${GREEN}✓ $pkg already installed${NC}"
    else
        echo -e "${YELLOW}Installing $pkg...${NC}"
        sudo apt-get install -y "$pkg"
    fi
done

echo ""
echo -e "${BLUE}[2/6] Setting up Python virtual environment...${NC}"
echo ""

if [ -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment already exists${NC}"
    read -p "Recreate it? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        echo -e "${GREEN}✓ Virtual environment recreated${NC}"
    fi
else
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate venv
source venv/bin/activate

echo ""
echo -e "${BLUE}[3/6] Upgrading pip...${NC}"
echo ""
pip install --upgrade pip

echo ""
echo -e "${BLUE}[4/6] Installing Python packages...${NC}"
echo -e "${YELLOW}(This may take 5-10 minutes for first-time installation)${NC}"
echo ""

# Install PyTorch with CUDA first
echo "Installing PyTorch with CUDA support..."
pip install torch==2.5.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu121

# Install other requirements
pip install -r requirements.txt

echo ""
echo -e "${GREEN}✓ Python packages installed${NC}"

echo ""
echo -e "${BLUE}[5/6] Verifying GPU access...${NC}"
echo ""

if python3 -c "import torch; print('CUDA available:', torch.cuda.is_available())" | grep -q "True"; then
    echo -e "${GREEN}✓ GPU detected and accessible!${NC}"
    python3 -c "import torch; print('  GPU:', torch.cuda.get_device_name(0))"
else
    echo -e "${YELLOW}! GPU not detected${NC}"
    echo "  Transcription will work but may be slower"
    echo "  Make sure NVIDIA drivers are installed: nvidia-smi"
fi

echo ""
echo -e "${BLUE}[6/6] Setting up Ollama (optional)...${NC}"
echo ""

if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✓ Ollama already installed${NC}"
    
    # Check if running
    if systemctl is-active --quiet ollama 2>/dev/null || pgrep -x ollama > /dev/null; then
        echo -e "${GREEN}✓ Ollama is running${NC}"
    else
        echo -e "${YELLOW}! Ollama not running${NC}"
        echo "  Start with: sudo systemctl start ollama"
        echo "  Or run: ollama serve &"
    fi
    
    echo ""
    read -p "Pull llama3.2 model? (recommended, ~2GB) (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ollama pull llama3.2
        echo -e "${GREEN}✓ Model downloaded${NC}"
    fi
    
else
    echo -e "${YELLOW}Ollama not found${NC}"
    echo ""
    read -p "Install Ollama for AI summaries? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Installing Ollama..."
        curl -fsSL https://ollama.ai/install.sh | sh
        
        # Give it a moment to start
        sleep 2
        
        # Pull default model
        echo "Downloading llama3.2 model..."
        ollama pull llama3.2
        
        echo -e "${GREEN}✓ Ollama installed${NC}"
    else
        echo "Skipping Ollama. You can install it later with:"
        echo "  curl -fsSL https://ollama.ai/install.sh | sh"
    fi
fi

echo ""
echo -e "${BLUE}[Setup Complete] Creating project structure...${NC}"
echo ""

# Create directories
mkdir -p input
mkdir -p output

# Make scripts executable
chmod +x run_transcribe.sh 2>/dev/null || true
chmod +x check_system.sh 2>/dev/null || true
chmod +x select_ollama_model.sh 2>/dev/null || true
chmod +x install.sh 2>/dev/null || true

echo -e "${GREEN}✓ Directories created${NC}"
echo -e "${GREEN}✓ Scripts made executable${NC}"

echo ""
echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║                  ✅ Installation Complete! ✅                  ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

echo -e "${BLUE}📁 Project Structure:${NC}"
echo "  input/          - Place your audio/PDF files here"
echo "  output/         - Processed files (optional)"
echo "  config.yaml     - Main configuration"
echo "  venv/           - Python environment"
echo ""

echo -e "${BLUE}🚀 Quick Start:${NC}"
echo "  1. Add files:     cp your_audio.mp3 input/"
echo "  2. Run:           ./run_transcribe.sh"
echo "  3. Check output:  ls input/"
echo ""

echo -e "${BLUE}🛠️ Useful Commands:${NC}"
echo "  Check system:     ./check_system.sh"
echo "  Change AI model:  ./select_ollama_model.sh"
echo "  Edit config:      nano config.yaml"
echo ""

echo -e "${BLUE}📚 Documentation:${NC}"
echo "  Quick start:      cat QUICK_START.md"
echo "  Full guide:       cat README.md"
echo "  Config examples:  cat config_examples.md"
echo ""

# Run system check
echo -e "${YELLOW}Running system check...${NC}"
echo ""
./check_system.sh

echo ""
echo -e "${GREEN}Ready to transcribe! 🎙️→📝${NC}"
echo ""