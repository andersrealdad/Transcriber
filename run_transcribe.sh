#!/bin/bash

###############################################################################
# Audio Transcription and PDF OCR Processing Script
# Usage: ./run_transcribe.sh [config_file]
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default config file
CONFIG_FILE="${1:-config.yaml}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Audio Transcription & OCR Processing${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Make helper scripts executable
chmod +x check_system.sh 2>/dev/null || true
chmod +x select_ollama_model.sh 2>/dev/null || true
chmod +x monitor_progress.sh 2>/dev/null || true

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}Error: Config file '$CONFIG_FILE' not found!${NC}"
    echo "Usage: $0 [config_file]"
    exit 1
fi

echo -e "${YELLOW}Using config file: $CONFIG_FILE${NC}"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 not found!${NC}"
    exit 1
fi

# Check if CUDA is available (optional but recommended)
echo -e "${YELLOW}Checking GPU availability...${NC}"
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
    echo ""
else
    echo -e "${YELLOW}Warning: nvidia-smi not found. GPU acceleration may not work.${NC}"
    echo ""
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating one...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}Virtual environment created!${NC}"
    echo ""
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Check if requirements are installed
if [ ! -f ".requirements_installed" ]; then
    echo -e "${YELLOW}Installing requirements...${NC}"
    pip install --upgrade pip
    pip install -r requirements.txt
    touch .requirements_installed
    echo -e "${GREEN}Requirements installed!${NC}"
    echo ""
else
    echo -e "${GREEN}Requirements already installed (delete .requirements_installed to reinstall)${NC}"
    echo ""
fi

# Install Tesseract OCR language data if not present
echo -e "${YELLOW}Checking Tesseract language data...${NC}"
if ! tesseract --list-langs 2>/dev/null | grep -q "nor"; then
    echo -e "${YELLOW}Norwegian language data not found for Tesseract.${NC}"
    echo -e "${YELLOW}Install it with: sudo apt-get install tesseract-ocr-nor${NC}"
    echo ""
fi

# Run the transcription script
echo -e "${GREEN}Starting transcription and OCR processing...${NC}"
echo ""
python3 transcribe.py "$CONFIG_FILE"

# Check exit status
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Processing completed successfully!${NC}"
    echo -e "${GREEN}========================================${NC}"
else
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}Processing failed!${NC}"
    echo -e "${RED}========================================${NC}"
    exit 1
fi
