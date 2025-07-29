#!/bin/bash
# Generate comprehensive TensorFlow Java API documentation
# This script addresses issue #96799 by ensuring up-to-date TensorFlow Java
# documentation is generated for tensorflow.org

set -e

# Default values
OUTPUT_DIR="/tmp/tf_java_docs"
SITE_PATH="java/api_docs/java"
TENSORFLOW_JAVA_REPO=""
VERBOSE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --output-dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --site-path)
      SITE_PATH="$2"
      shift 2
      ;;
    --tensorflow-java-repo)
      TENSORFLOW_JAVA_REPO="$2"
      shift 2
      ;;
    --verbose)
      VERBOSE=true
      shift
      ;;
    --help)
      echo "Usage: $0 [OPTIONS]"
      echo ""
      echo "Generate comprehensive TensorFlow Java API documentation"
      echo ""
      echo "Options:"
      echo "  --output-dir DIR          Output directory for generated docs"
      echo "  --site-path PATH          Site path for _toc.yaml"
      echo "  --tensorflow-java-repo    Path to local TensorFlow Java repository"
      echo "  --verbose                 Enable verbose output"
      echo "  --help                    Show this help message"
      echo ""
      echo "This script addresses TensorFlow issue #96799 by generating"
      echo "documentation for TensorFlow Java v1.1.0 instead of outdated v0.3.3"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
TENSORFLOW_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

if [ "$VERBOSE" = true ]; then
  echo "TensorFlow Java Documentation Generator"
  echo "======================================"
  echo "TensorFlow root: $TENSORFLOW_ROOT"
  echo "Output directory: $OUTPUT_DIR"
  echo "Site path: $SITE_PATH"
  echo "TensorFlow Java repo: ${TENSORFLOW_JAVA_REPO:-"(will be cloned automatically)"}"
  echo ""
fi

# Ensure output directory exists
mkdir -p "$OUTPUT_DIR"

# Build the documentation
echo "Generating TensorFlow Java documentation..."

cd "$TENSORFLOW_ROOT"

PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

# Prepare arguments
ARGS=(
    "tensorflow/tools/docs/build_comprehensive_java_api_docs.py"
    "--output_dir=$OUTPUT_DIR"
    "--site_path=$SITE_PATH"
)

if [ -n "$TENSORFLOW_JAVA_REPO" ]; then
    ARGS+=("--tensorflow_java_repo=$TENSORFLOW_JAVA_REPO")
fi

# Run the documentation generator
if [ "$VERBOSE" = true ]; then
    echo "Running: $PYTHON_CMD ${ARGS[*]}"
    echo ""
fi

"$PYTHON_CMD" "${ARGS[@]}"

echo ""
echo "Documentation generation completed!"
echo "Output directory: $OUTPUT_DIR"
echo ""
echo "This documentation reflects TensorFlow Java v1.1.0 (current)"
echo "and addresses issue #96799 (outdated v0.3.3 documentation)"
