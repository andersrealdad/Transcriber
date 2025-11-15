#!/bin/bash

###############################################################################
# Ollama Model Selector - Easy way to change summarization model
###############################################################################

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

CONFIG_FILE="config.yaml"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Ollama Model Selector${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check if Ollama is available
if ! command -v ollama &> /dev/null; then
    echo -e "${YELLOW}Ollama not found!${NC}"
    echo "Install: curl -fsSL https://ollama.ai/install.sh | sh"
    exit 1
fi

# List available models
echo -e "${GREEN}Available models on your system:${NC}"
echo ""

models=($(ollama list 2>/dev/null | tail -n +2 | awk '{print $1}'))

if [ ${#models[@]} -eq 0 ]; then
    echo -e "${YELLOW}No models installed yet!${NC}"
    echo ""
    echo "Popular models for summarization:"
    echo "  ollama pull llama3.2      # Fast, good quality (recommended)"
    echo "  ollama pull llama3.1      # Larger, better summaries"
    echo "  ollama pull mistral       # Excellent multilingual"
    echo "  ollama pull gemma2        # Good balance"
    echo "  ollama pull qwen2.5       # Strong Norwegian support"
    echo ""
    exit 1
fi

# Display models with numbers
for i in "${!models[@]}"; do
    model="${models[$i]}"
    
    # Get model info
    size=$(ollama list 2>/dev/null | grep "^$model" | awk '{print $2}')
    
    # Add descriptions for common models
    desc=""
    case "$model" in
        llama3.2*)
            desc="- Fast, efficient (recommended)"
            ;;
        llama3.1*)
            desc="- Larger, better for complex summaries"
            ;;
        mistral*)
            desc="- Excellent multilingual support"
            ;;
        gemma2*)
            desc="- Good balance of speed/quality"
            ;;
        qwen2.5*)
            desc="- Strong Norwegian support"
            ;;
    esac
    
    echo -e "  [$((i+1))] ${GREEN}$model${NC} ($size) $desc"
done

echo ""
echo -e "  [0] Pull a new model"
echo ""

# Get current model from config
current_model=$(grep "model:" "$CONFIG_FILE" | grep -v "#" | head -1 | sed 's/.*model: *"\?\([^"]*\)"\?.*/\1/')
if [ -n "$current_model" ]; then
    echo -e "Current model in config: ${YELLOW}$current_model${NC}"
    echo ""
fi

# Prompt for selection
read -p "Select model number: " selection

if [ "$selection" = "0" ]; then
    echo ""
    echo "Popular models:"
    echo "  - llama3.2 (recommended, ~2GB)"
    echo "  - llama3.1 (better quality, ~5GB)"
    echo "  - mistral (multilingual, ~4GB)"
    echo "  - gemma2 (balanced, ~5GB)"
    echo "  - qwen2.5 (Norwegian, ~4GB)"
    echo ""
    read -p "Enter model name to pull: " model_name
    
    if [ -n "$model_name" ]; then
        echo ""
        echo -e "${YELLOW}Pulling $model_name...${NC}"
        ollama pull "$model_name"
        
        if [ $? -eq 0 ]; then
            selected_model="$model_name"
        else
            echo -e "${YELLOW}Failed to pull model${NC}"
            exit 1
        fi
    else
        exit 0
    fi
elif [ "$selection" -ge 1 ] && [ "$selection" -le "${#models[@]}" ]; then
    selected_model="${models[$((selection-1))]}"
else
    echo "Invalid selection"
    exit 1
fi

# Update config.yaml
echo ""
echo -e "${YELLOW}Updating config.yaml...${NC}"

# Use sed to update the model line
sed -i "s/model: *\".*\"/model: \"$selected_model\"/" "$CONFIG_FILE"
sed -i "s/model: *[a-zA-Z0-9._-]*/model: \"$selected_model\"/" "$CONFIG_FILE"

echo -e "${GREEN}✓ Model updated to: $selected_model${NC}"
echo ""

# Test the model
echo -e "${YELLOW}Testing model...${NC}"
echo ""

test_response=$(ollama run "$selected_model" "Say 'OK' in one word" 2>/dev/null | head -1)

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Model is working!${NC}"
    echo ""
    echo "Response: $test_response"
else
    echo -e "${YELLOW}! Model might need a moment to load${NC}"
fi

echo ""
echo -e "${GREEN}Ready to use!${NC}"
echo "Run: ./run_transcribe.sh"
echo ""