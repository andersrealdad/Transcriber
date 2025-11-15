#!/bin/bash

###############################################################################
# System Check Script - Verify all dependencies are ready
###############################################################################

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}System Requirements Check${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check GPU
echo -e "${YELLOW}[1/8] Checking GPU...${NC}"
if command -v nvidia-smi &> /dev/null; then
    echo -e "${GREEN}✓ NVIDIA GPU detected${NC}"
    nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
    echo ""
else
    echo -e "${RED}✗ nvidia-smi not found - GPU acceleration may not work${NC}"
    echo ""
fi

# Check Python
echo -e "${YELLOW}[2/8] Checking Python...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi
echo ""

# Check FFmpeg
echo -e "${YELLOW}[3/8] Checking FFmpeg...${NC}"
if command -v ffmpeg &> /dev/null; then
    FFMPEG_VERSION=$(ffmpeg -version | head -n1)
    echo -e "${GREEN}✓ $FFMPEG_VERSION${NC}"
else
    echo -e "${RED}✗ FFmpeg not found${NC}"
    echo "Install: sudo apt-get install ffmpeg"
fi
echo ""

# Check Tesseract
echo -e "${YELLOW}[4/8] Checking Tesseract OCR...${NC}"
if command -v tesseract &> /dev/null; then
    TESS_VERSION=$(tesseract --version | head -n1)
    echo -e "${GREEN}✓ $TESS_VERSION${NC}"
    
    # Check languages
    echo -e "${BLUE}  Available languages:${NC}"
    tesseract --list-langs 2>/dev/null | tail -n +2 | while read lang; do
        if [[ "$lang" == "eng" || "$lang" == "nor" ]]; then
            echo -e "  ${GREEN}✓ $lang${NC}"
        else
            echo -e "  - $lang"
        fi
    done
    
    if ! tesseract --list-langs 2>/dev/null | grep -q "eng"; then
        echo -e "${YELLOW}  ! English not found - install: sudo apt-get install tesseract-ocr-eng${NC}"
    fi
    if ! tesseract --list-langs 2>/dev/null | grep -q "nor"; then
        echo -e "${YELLOW}  ! Norwegian not found - install: sudo apt-get install tesseract-ocr-nor${NC}"
    fi
else
    echo -e "${RED}✗ Tesseract not found${NC}"
    echo "Install: sudo apt-get install tesseract-ocr tesseract-ocr-eng tesseract-ocr-nor"
fi
echo ""

# Check poppler (for PDF)
echo -e "${YELLOW}[5/8] Checking Poppler (PDF support)...${NC}"
if command -v pdftoppm &> /dev/null; then
    echo -e "${GREEN}✓ Poppler installed${NC}"
else
    echo -e "${RED}✗ Poppler not found${NC}"
    echo "Install: sudo apt-get install poppler-utils"
fi
echo ""

# Check Ollama
echo -e "${YELLOW}[6/8] Checking Ollama...${NC}"
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✓ Ollama installed${NC}"
    
    # Check if running
    if systemctl is-active --quiet ollama 2>/dev/null || pgrep -x ollama > /dev/null; then
        echo -e "${GREEN}✓ Ollama is running${NC}"
        
        # List models
        echo -e "${BLUE}  Available models:${NC}"
        ollama list 2>/dev/null | tail -n +2 | while read -r line; do
            model_name=$(echo "$line" | awk '{print $1}')
            echo -e "  ${GREEN}✓ $model_name${NC}"
        done
        
        # Check for recommended models
        if ! ollama list 2>/dev/null | grep -q "llama3.2"; then
            echo -e "${YELLOW}  ! Recommended: ollama pull llama3.2${NC}"
        fi
    else
        echo -e "${YELLOW}! Ollama installed but not running${NC}"
        echo "  Start: sudo systemctl start ollama"
        echo "  Or run: ollama serve &"
    fi
else
    echo -e "${YELLOW}! Ollama not found (optional for summaries)${NC}"
    echo "  Install: curl -fsSL https://ollama.ai/install.sh | sh"
fi
echo ""

# Check Python packages
echo -e "${YELLOW}[7/8] Checking Python packages...${NC}"
if [ -d "venv" ]; then
    source venv/bin/activate
    echo -e "${GREEN}✓ Virtual environment found${NC}"
    
    # Check key packages
    for pkg in "faster-whisper" "torch" "demucs" "deepfilternet" "pytesseract"; do
        if python3 -c "import ${pkg//-/_}" 2>/dev/null; then
            echo -e "  ${GREEN}✓ $pkg${NC}"
        else
            echo -e "  ${YELLOW}! $pkg not installed${NC}"
        fi
    done
else
    echo -e "${YELLOW}! Virtual environment not found${NC}"
    echo "  Run: ./run_transcribe.sh (will create automatically)"
fi
echo ""

# Check CUDA
echo -e "${YELLOW}[8/8] Checking CUDA...${NC}"
if python3 -c "import torch; print('CUDA available:', torch.cuda.is_available())" 2>/dev/null | grep -q "True"; then
    echo -e "${GREEN}✓ CUDA available in PyTorch${NC}"
    python3 -c "import torch; print('  Device:', torch.cuda.get_device_name(0))" 2>/dev/null
else
    echo -e "${YELLOW}! CUDA not available in PyTorch${NC}"
    echo "  This is normal if packages aren't installed yet"
fi
echo ""

# Summary
echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Summary${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

MISSING=0

# Required
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 (REQUIRED)${NC}"
    MISSING=$((MISSING + 1))
fi
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${RED}✗ FFmpeg (REQUIRED)${NC}"
    MISSING=$((MISSING + 1))
fi

# Optional but recommended
if ! command -v nvidia-smi &> /dev/null; then
    echo -e "${YELLOW}! GPU drivers (recommended for speed)${NC}"
fi
if ! command -v tesseract &> /dev/null; then
    echo -e "${YELLOW}! Tesseract (required for PDF OCR)${NC}"
fi
if ! command -v ollama &> /dev/null; then
    echo -e "${YELLOW}! Ollama (optional, for summaries)${NC}"
fi

echo ""
if [ $MISSING -eq 0 ]; then
    echo -e "${GREEN}✓ All required dependencies found!${NC}"
    echo -e "${GREEN}  Ready to run: ./run_transcribe.sh${NC}"
else
    echo -e "${RED}✗ Missing $MISSING required dependencies${NC}"
    echo -e "${YELLOW}  Install missing items above${NC}"
fi
echo ""