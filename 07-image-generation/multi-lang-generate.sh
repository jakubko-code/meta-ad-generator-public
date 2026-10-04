#!/bin/bash
#
# Multi-Language Orchestrator pre generate_ads.py
# Spustí batch generation paralelne pre všetky cieľové jazyky.
#
# Filozofia:
#   - Každý batch job ide do Google API samostatne, polluje sa nezávisle
#   - 5 jazykov × 30 min batch = 30 min total (paralelne) vs 2.5h (sequentially)
#   - Logy per jazyk pre tracking
#
# Usage:
#   ./multi-lang-generate.sh \
#     --brand-dir "brands/gymbeam/products/melatonin-plus-yummies/product-image-ads-motion/2026-05-05-gymbeam-templates" \
#     --languages cz,hu,ro,de,en \
#     --images-dir "/abs/path/to/source-product-images" \
#     [--provider google-batch] \
#     [--prompts-pattern "prompts-{lang}.json"] \
#     [--output-pattern "outputs-{lang}"]
#
# Required env: GEMINI_API_KEY (alebo FAL_KEY pre fal provider)

set -e

# Defaults
PROVIDER="google-batch"
PROMPTS_PATTERN="prompts-{lang}.json"
OUTPUT_PATTERN="outputs-{lang}"
SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/generate_ads.py"

usage() {
    cat <<EOF
Multi-Language Orchestrator pre generate_ads.py

Usage:
  $0 \\
    --brand-dir DIR \\
    --languages LANG1,LANG2,... \\
    --images-dir DIR \\
    [--provider google-batch|google|fal]   (default: google-batch)
    [--prompts-pattern "prompts-{lang}.json"] \\
    [--output-pattern "outputs-{lang}"]

Examples:
  # 5 jazykov paralelne cez Google Batch
  $0 \\
    --brand-dir "brands/gymbeam/products/melatonin-plus-yummies/product-image-ads-motion/2026-05-05" \\
    --languages cz,hu,ro,de,en \\
    --images-dir "/abs/path/source-product-images"

  # 16 trhov pre full EU campaign
  $0 \\
    --brand-dir "brands/gymbeam/products/X/.../{date}" \\
    --languages sk,cz,hu,ro,de,pl,hr,bg,rs,si,at,it,es,fr,nl,en \\
    --images-dir "..."
EOF
    exit 1
}

# Parse args
BRAND_DIR=""
LANGUAGES=""
IMAGES_DIR=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --brand-dir)        BRAND_DIR="$2"; shift 2 ;;
        --languages)        LANGUAGES="$2"; shift 2 ;;
        --images-dir)       IMAGES_DIR="$2"; shift 2 ;;
        --provider)         PROVIDER="$2"; shift 2 ;;
        --prompts-pattern)  PROMPTS_PATTERN="$2"; shift 2 ;;
        --output-pattern)   OUTPUT_PATTERN="$2"; shift 2 ;;
        -h|--help)          usage ;;
        *) echo "Unknown arg: $1"; usage ;;
    esac
done

# Validation
[[ -z "$BRAND_DIR" ]] && { echo "Error: --brand-dir required"; usage; }
[[ -z "$LANGUAGES" ]] && { echo "Error: --languages required"; usage; }
[[ -z "$IMAGES_DIR" ]] && { echo "Error: --images-dir required"; usage; }
[[ ! -d "$BRAND_DIR" ]] && { echo "Error: brand-dir does not exist: $BRAND_DIR"; exit 1; }
[[ ! -f "$SCRIPT_PATH" ]] && { echo "Error: generate_ads.py not found at $SCRIPT_PATH"; exit 1; }

# Setup logs dir
LOGS_DIR="$BRAND_DIR/logs"
mkdir -p "$LOGS_DIR"

# Parse languages
IFS=',' read -ra LANG_ARRAY <<< "$LANGUAGES"
LANG_COUNT=${#LANG_ARRAY[@]}

# Banner
echo "============================================================"
echo "  Multi-Language Orchestrator"
echo "  Brand dir:       $BRAND_DIR"
echo "  Languages:       ${LANG_COUNT} (${LANG_ARRAY[*]})"
echo "  Provider:        $PROVIDER"
echo "  Prompts pattern: $PROMPTS_PATTERN"
echo "  Output pattern:  $OUTPUT_PATTERN"
echo "  Images dir:      $IMAGES_DIR"
echo "  Logs dir:        $LOGS_DIR"
echo "============================================================"
echo ""

# Pre-flight: skontroluj že každý prompts-{lang}.json existuje
MISSING_FILES=()
for lang in "${LANG_ARRAY[@]}"; do
    prompts_file="${PROMPTS_PATTERN/\{lang\}/$lang}"
    full_path="$BRAND_DIR/$prompts_file"
    if [[ ! -f "$full_path" ]]; then
        MISSING_FILES+=("$full_path")
    fi
done

if [[ ${#MISSING_FILES[@]} -gt 0 ]]; then
    echo "✗ Chýbajú prompts files pre niektoré jazyky:"
    for f in "${MISSING_FILES[@]}"; do
        echo "    $f"
    done
    echo ""
    echo "Najprv vyrob prompts-{lang}.json cez Copy Translator (BONUS/04)."
    exit 1
fi

echo "✓ Všetky prompts-{lang}.json existujú."
echo ""

# Spusti batch jobs paralelne
echo "Spúšťam $LANG_COUNT paralelných jobov..."
echo ""

# Indexed arrays work on macOS' system Bash 3.2 as well as newer Bash versions.
JOB_PIDS=()
JOB_LOGS=()
JOB_LANGS=()

START_TIME=$(date +%s)

for lang in "${LANG_ARRAY[@]}"; do
    prompts_file="${PROMPTS_PATTERN/\{lang\}/$lang}"
    output_dir="${OUTPUT_PATTERN/\{lang\}/$lang}"
    log_file="$LOGS_DIR/gen-${lang}-$(date +%Y%m%d-%H%M%S).log"

    # --lang musí ísť do skriptu: riadi pre-flight kontrolu cien pre daný trh
    # Cena prenesená zo SK je povolená len ak approval-{lang}.json explicitne obsahuje
    # market_prices_confirmed=true. Generátor je neinteraktívny a pri chýbajúcom gate spadne.
    python3 "$SCRIPT_PATH" \
        --provider "$PROVIDER" \
        --brand-dir "$BRAND_DIR" \
        --prompts-file "$prompts_file" \
        --images-dir "$IMAGES_DIR" \
        --output-dir "$output_dir" \
        --lang "$lang" \
        < /dev/null > "$log_file" 2>&1 &

    pid=$!
    JOB_PIDS+=("$pid")
    JOB_LOGS+=("$log_file")
    JOB_LANGS+=("$lang")

    echo "  → [$lang] PID $pid · log: $log_file"
done

echo ""
echo "Všetky joby spustené. Čakám na dokončenie..."
echo ""

# Track completion
SUCCESS=()
FAILED=()

for i in "${!JOB_PIDS[@]}"; do
    lang=${JOB_LANGS[$i]}
    pid=${JOB_PIDS[$i]}
    log=${JOB_LOGS[$i]}

    if wait "$pid"; then
        # Parse log for success indicator
        if grep -q "Generation Complete" "$log" 2>/dev/null; then
            completed=$(grep -oE "Completed: [0-9]+/[0-9]+" "$log" | tail -1)
            elapsed=$(($(date +%s) - START_TIME))
            echo "  ✓ [$lang] DONE — $completed (after ${elapsed}s)"
            SUCCESS+=("$lang")
        else
            echo "  ⚠ [$lang] exited 0 ale log neukazuje 'Generation Complete' — over $log"
            FAILED+=("$lang")
        fi
    else
        echo "  ✗ [$lang] FAILED — pozri $log"
        FAILED+=("$lang")
    fi
done

TOTAL_TIME=$(($(date +%s) - START_TIME))

# Summary
echo ""
echo "============================================================"
echo "  ORCHESTRATION SUMMARY"
echo "============================================================"
echo "  Total time:  ${TOTAL_TIME}s ($(($TOTAL_TIME/60))m $(($TOTAL_TIME%60))s)"
echo "  Successful:  ${#SUCCESS[@]}/${LANG_COUNT}"
echo "  Failed:      ${#FAILED[@]}/${LANG_COUNT}"
echo ""

if [[ ${#SUCCESS[@]} -gt 0 ]]; then
    echo "  ✓ Languages completed:"
    for lang in "${SUCCESS[@]}"; do
        output_path="${OUTPUT_PATTERN/\{lang\}/$lang}"
        echo "      $lang → $BRAND_DIR/$output_path/"
    done
fi

if [[ ${#FAILED[@]} -gt 0 ]]; then
    echo ""
    echo "  ✗ Failed languages (re-run individually after fix):"
    for lang in "${FAILED[@]}"; do
        for i in "${!JOB_LANGS[@]}"; do
            if [[ "${JOB_LANGS[$i]}" == "$lang" ]]; then
                echo "      $lang → log: ${JOB_LOGS[$i]}"
                break
            fi
        done
    done
    exit 1
fi

echo "============================================================"
echo "  Všetky jazyky kompletne vygenerované."
echo "============================================================"
