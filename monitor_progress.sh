#!/bin/bash

###############################################################################
# Progress Monitor for Batch Transcription
# Shows real-time progress of your transcription job
###############################################################################

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
INPUT_DIR="${1:-input}"
CHECK_INTERVAL=30  # seconds

if [ ! -d "$INPUT_DIR" ]; then
    echo "Error: Directory '$INPUT_DIR' not found"
    echo "Usage: $0 [input_directory]"
    exit 1
fi

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              Transcription Progress Monitor                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Monitoring: $INPUT_DIR"
echo "Update interval: ${CHECK_INTERVAL}s"
echo "Press Ctrl+C to stop"
echo ""

# Function to count files
count_files() {
    local pattern=$1
    find "$INPUT_DIR" -type f -name "$pattern" 2>/dev/null | wc -l
}

# Initial counts
total_audio=$(count_files "*.mp3") 
total_audio=$((total_audio + $(count_files "*.wav")))
total_audio=$((total_audio + $(count_files "*.m4a")))
total_audio=$((total_audio + $(count_files "*.flac")))
total_audio=$((total_audio + $(count_files "*.ogg")))
total_audio=$((total_audio + $(count_files "*.mp4")))
total_audio=$((total_audio + $(count_files "*.webm")))

total_pdf=$(count_files "*.pdf")

echo -e "${CYAN}Found:${NC}"
echo "  Audio files: $total_audio"
echo "  PDF files: $total_pdf"
echo ""

# Track start time
start_time=$(date +%s)

# Monitor loop
while true; do
    clear
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║              Transcription Progress Monitor                    ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Current time
    current_time=$(date +"%H:%M:%S")
    elapsed=$(($(date +%s) - start_time))
    elapsed_formatted=$(printf '%02d:%02d:%02d' $((elapsed/3600)) $((elapsed%3600/60)) $((elapsed%60)))
    
    echo -e "${CYAN}Current Time:${NC} $current_time"
    echo -e "${CYAN}Elapsed Time:${NC} $elapsed_formatted"
    echo ""
    
    # Count completed files
    completed_txt=$(count_files "*.txt")
    completed_md=$(count_files "*.md")
    
    # Count multi-pass files (if any)
    multipass_none=$(count_files "*_none.txt")
    multipass_demucs=$(count_files "*_demucs.txt")
    multipass_deep=$(count_files "*_deepfilternet.txt")
    multipass_both=$(count_files "*_both.txt")
    
    # Determine if multi-pass is being used
    if [ $multipass_none -gt 0 ] || [ $multipass_demucs -gt 0 ]; then
        using_multipass=true
        # In multi-pass, each audio creates 5 txt files (4 individual + 1 merged)
        # So completed audio = (total_txt - multi_pass_files) / 1, but we need merged ones
        completed_audio=$(count_files "*.txt" | xargs -I {} expr {} - $multipass_none - $multipass_demucs - $multipass_deep - $multipass_both)
        
        # Alternative: count files that don't have _strategy suffix
        completed_audio=$(find "$INPUT_DIR" -type f -name "*.txt" ! -name "*_none.txt" ! -name "*_demucs.txt" ! -name "*_deepfilternet.txt" ! -name "*_both.txt" 2>/dev/null | wc -l)
        
        # Subtract PDF results
        completed_audio=$((completed_audio - total_pdf))
        completed_audio=$((completed_audio < 0 ? 0 : completed_audio))
    else
        using_multipass=false
        # Standard: completed = txt files - pdf files
        completed_audio=$((completed_txt - total_pdf))
        completed_audio=$((completed_audio < 0 ? 0 : completed_audio))
    fi
    
    # Calculate percentages
    if [ $total_audio -gt 0 ]; then
        audio_pct=$((completed_audio * 100 / total_audio))
    else
        audio_pct=0
    fi
    
    if [ $total_pdf -gt 0 ]; then
        pdf_completed=$((completed_txt - completed_audio))
        pdf_completed=$((pdf_completed < 0 ? 0 : pdf_completed))
        pdf_pct=$((pdf_completed * 100 / total_pdf))
    else
        pdf_completed=0
        pdf_pct=0
    fi
    
    # Audio Progress
    echo -e "${GREEN}═══ AUDIO TRANSCRIPTION ═══${NC}"
    echo -e "Completed: ${GREEN}$completed_audio${NC} / $total_audio"
    echo -ne "Progress:  ["
    
    # Draw progress bar
    bar_width=40
    filled=$((audio_pct * bar_width / 100))
    for ((i=0; i<bar_width; i++)); do
        if [ $i -lt $filled ]; then
            echo -ne "${GREEN}█${NC}"
        else
            echo -ne "░"
        fi
    done
    echo -e "] ${GREEN}${audio_pct}%${NC}"
    
    # Multi-pass details
    if [ "$using_multipass" = true ]; then
        echo ""
        echo -e "${CYAN}Multi-Pass Progress:${NC}"
        echo "  Pass 1 (none):        $multipass_none files"
        echo "  Pass 2 (demucs):      $multipass_demucs files"
        echo "  Pass 3 (deepfilternet): $multipass_deep files"
        echo "  Pass 4 (both):        $multipass_both files"
    fi
    
    echo ""
    
    # PDF Progress (if any)
    if [ $total_pdf -gt 0 ]; then
        echo -e "${GREEN}═══ PDF OCR ═══${NC}"
        echo -e "Completed: ${GREEN}$pdf_completed${NC} / $total_pdf"
        echo -ne "Progress:  ["
        
        filled=$((pdf_pct * bar_width / 100))
        for ((i=0; i<bar_width; i++)); do
            if [ $i -lt $filled ]; then
                echo -ne "${GREEN}█${NC}"
            else
                echo -ne "░"
            fi
        done
        echo -e "] ${GREEN}${pdf_pct}%${NC}"
        echo ""
    fi
    
    # Summaries
    echo -e "${GREEN}═══ SUMMARIES ═══${NC}"
    echo -e "Completed: ${GREEN}$completed_md${NC} / $completed_audio expected"
    echo ""
    
    # Estimate completion time
    if [ $completed_audio -gt 0 ] && [ $audio_pct -lt 100 ]; then
        avg_time_per_file=$((elapsed / completed_audio))
        remaining_files=$((total_audio - completed_audio))
        estimated_remaining=$((avg_time_per_file * remaining_files))
        
        est_hours=$((estimated_remaining / 3600))
        est_mins=$(( (estimated_remaining % 3600) / 60))
        
        echo -e "${YELLOW}═══ ESTIMATE ═══${NC}"
        echo "Avg time per file: $(printf '%d:%02d' $((avg_time_per_file/60)) $((avg_time_per_file%60)))"
        echo "Estimated remaining: ${est_hours}h ${est_mins}m"
        
        # Calculate ETA
        eta_timestamp=$(($(date +%s) + estimated_remaining))
        eta_time=$(date -d @$eta_timestamp +"%H:%M:%S")
        echo "Estimated completion: $eta_time"
        echo ""
    fi
    
    # Recent files
    echo -e "${CYAN}═══ RECENT COMPLETIONS ═══${NC}"
    find "$INPUT_DIR" -type f -name "*.txt" ! -name "*_none.txt" ! -name "*_demucs.txt" ! -name "*_deepfilternet.txt" ! -name "*_both.txt" -printf '%T@ %p\n' 2>/dev/null | \
        sort -rn | head -3 | cut -d' ' -f2- | while read -r file; do
        echo "  ✓ $(basename "$file")"
    done
    echo ""
    
    # Status
    if [ $audio_pct -eq 100 ] && [ $pdf_pct -eq 100 ]; then
        echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║   ✓ ALL PROCESSING COMPLETE! ✓        ║${NC}"
        echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
        echo ""
        echo "Total time: $elapsed_formatted"
        break
    fi
    
    echo -e "${YELLOW}Updating in ${CHECK_INTERVAL}s... (Ctrl+C to stop)${NC}"
    
    sleep $CHECK_INTERVAL
done