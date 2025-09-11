#!/bin/bash

# AnythingLLM Feature Map Verification Script
# Validates paths, providers, and dependencies listed in the feature map

set -e

FEATURE_MAP="hd-docs/system-overview/feature-map.md"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 Verifying AnythingLLM Feature Map..."
echo "📄 Document: $FEATURE_MAP"
echo

# Check if feature map exists
if [ ! -f "$FEATURE_MAP" ]; then
    echo -e "${RED}❌ Feature map not found: $FEATURE_MAP${NC}"
    exit 1
fi

# Extract frontmatter
REPO_COMMIT=$(grep "repo_commit:" "$FEATURE_MAP" | cut -d'"' -f2)
GENERATED_AT=$(grep "generated_at:" "$FEATURE_MAP" | cut -d'"' -f2)
VERSION=$(grep "version:" "$FEATURE_MAP" | cut -d'"' -f2)

echo -e "📋 Document metadata:"
echo -e "   Generated: $GENERATED_AT"
echo -e "   Commit: $REPO_COMMIT"
echo -e "   Version: $VERSION"
echo

# Verify current commit matches
CURRENT_COMMIT=$(git rev-parse HEAD)
if [ "$REPO_COMMIT" != "$CURRENT_COMMIT" ]; then
    echo -e "${YELLOW}⚠️  Warning: Document generated from different commit${NC}"
    echo -e "   Document commit: $REPO_COMMIT"
    echo -e "   Current commit:  $CURRENT_COMMIT"
    echo
fi

# Initialize counters
TOTAL_PATHS=0
MISSING_PATHS=0
TOTAL_PROVIDERS=0
MISSING_PROVIDERS=0

echo "🔍 Checking file paths..."

# Extract and verify file paths from the feature map
# Look for patterns like `/server/endpoints/chat.js`, `/frontend/src/components/WorkspaceChat/`
while IFS= read -r line; do
    if [[ $line =~ \*\*Files:\*\*[[:space:]]*\`([^\`]+)\` ]]; then
        PATHS="${BASH_REMATCH[1]}"
        # Split multiple paths by comma and clean them
        IFS=',' read -ra PATH_ARRAY <<< "$PATHS"
        for path in "${PATH_ARRAY[@]}"; do
            # Clean up the path (remove leading/trailing whitespace, leading slash)
            path=$(echo "$path" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//;s/^[\/]*//;s/[[:space:]]*$//')
            
            if [ -n "$path" ]; then
                TOTAL_PATHS=$((TOTAL_PATHS + 1))
                
                # Special handling for runtime directories and component-specific paths
                if [[ "$path" == *"(runtime: "* ]]; then
                    # Extract base path before the runtime note
                    base_path=$(echo "$path" | sed 's/ (runtime:.*//')
                    if [ -e "$base_path" ]; then
                        echo -e "${GREEN}✅ Found: $path ${YELLOW}(base path exists, runtime directory created as needed)${NC}"
                    else
                        echo -e "${RED}❌ Missing: $path${NC}"
                        MISSING_PATHS=$((MISSING_PATHS + 1))
                    fi
                elif [[ "$path" == "./"* ]]; then
                    # Handle relative paths starting with ./
                    actual_path="${path:2}"  # Remove the ./
                    if [ -e "$actual_path" ]; then
                        echo -e "${GREEN}✅ Found: $path${NC}"
                    else
                        echo -e "${RED}❌ Missing: $path${NC}"
                        MISSING_PATHS=$((MISSING_PATHS + 1))
                    fi
                else
                    # Check if path exists (file or directory)
                    if [ ! -e "$path" ]; then
                        echo -e "${RED}❌ Missing: $path${NC}"
                        MISSING_PATHS=$((MISSING_PATHS + 1))
                    else
                        echo -e "${GREEN}✅ Found: $path${NC}"
                    fi
                fi
            fi
        done
    fi
done < "$FEATURE_MAP"

echo
echo "🔍 Checking LLM providers..."

# Check LLM provider directories
PROVIDER_DIRS=(
    "server/utils/AiProviders/openAi"
    "server/utils/AiProviders/anthropic"
    "server/utils/AiProviders/azureOpenAi"
    "server/utils/AiProviders/bedrock"
    "server/utils/AiProviders/gemini"
    "server/utils/AiProviders/cohere"
    "server/utils/AiProviders/groq"
    "server/utils/AiProviders/ollama"
    "server/utils/AiProviders/lmStudio"
    "server/utils/AiProviders/localAi"
    "server/utils/AiProviders/textGenWebUI"
    "server/utils/AiProviders/koboldCPP"
    "server/utils/AiProviders/huggingface"
    "server/utils/AiProviders/fireworksAi"
    "server/utils/AiProviders/togetherAi"
    "server/utils/AiProviders/perplexity"
    "server/utils/AiProviders/openRouter"
    "server/utils/AiProviders/deepseek"
    "server/utils/AiProviders/mistral"
    "server/utils/AiProviders/xai"
    "server/utils/AiProviders/novita"
    "server/utils/AiProviders/nvidiaNim"
    "server/utils/AiProviders/moonshotAi"
    "server/utils/AiProviders/ppio"
    "server/utils/AiProviders/apipie"
    "server/utils/AiProviders/liteLLM"
    "server/utils/AiProviders/genericOpenAi"
)

for provider in "${PROVIDER_DIRS[@]}"; do
    TOTAL_PROVIDERS=$((TOTAL_PROVIDERS + 1))
    if [ ! -d "$provider" ]; then
        echo -e "${RED}❌ Missing provider: $provider${NC}"
        MISSING_PROVIDERS=$((MISSING_PROVIDERS + 1))
    else
        echo -e "${GREEN}✅ Found provider: $provider${NC}"
    fi
done

echo
echo "🔍 Checking vector database providers..."

# Check vector database providers
VECTOR_DB_DIRS=(
    "server/utils/vectorDbProviders/lance"
    "server/utils/vectorDbProviders/pinecone"
    "server/utils/vectorDbProviders/chroma"
    "server/utils/vectorDbProviders/chromacloud"
    "server/utils/vectorDbProviders/weaviate"
    "server/utils/vectorDbProviders/qdrant"
    "server/utils/vectorDbProviders/milvus"
    "server/utils/vectorDbProviders/zilliz"
    "server/utils/vectorDbProviders/astra"
    "server/utils/vectorDbProviders/pgvector"
)

TOTAL_VECTOR_DBS=0
MISSING_VECTOR_DBS=0

for vdb in "${VECTOR_DB_DIRS[@]}"; do
    TOTAL_VECTOR_DBS=$((TOTAL_VECTOR_DBS + 1))
    if [ ! -d "$vdb" ]; then
        echo -e "${RED}❌ Missing vector DB: $vdb${NC}"
        MISSING_VECTOR_DBS=$((MISSING_VECTOR_DBS + 1))
    else
        echo -e "${GREEN}✅ Found vector DB: $vdb${NC}"
    fi
done

echo
echo "🔍 Checking embedding engines..."

# Check embedding engines
EMBEDDING_DIRS=(
    "server/utils/EmbeddingEngines/native"
    "server/utils/EmbeddingEngines/openAi"
    "server/utils/EmbeddingEngines/azureOpenAi"
    "server/utils/EmbeddingEngines/cohere"
    "server/utils/EmbeddingEngines/ollama"
    "server/utils/EmbeddingEngines/lmstudio"
    "server/utils/EmbeddingEngines/localAi"
    "server/utils/EmbeddingEngines/gemini"
    "server/utils/EmbeddingEngines/voyageAi"
    "server/utils/EmbeddingEngines/mistral"
    "server/utils/EmbeddingEngines/liteLLM"
    "server/utils/EmbeddingEngines/genericOpenAi"
)

TOTAL_EMBEDDINGS=0
MISSING_EMBEDDINGS=0

for emb in "${EMBEDDING_DIRS[@]}"; do
    TOTAL_EMBEDDINGS=$((TOTAL_EMBEDDINGS + 1))
    if [ ! -d "$emb" ]; then
        echo -e "${RED}❌ Missing embedding engine: $emb${NC}"
        MISSING_EMBEDDINGS=$((MISSING_EMBEDDINGS + 1))
    else
        echo -e "${GREEN}✅ Found embedding engine: $emb${NC}"
    fi
done

echo
echo "🔍 Checking key dependencies..."

# Check key package.json files exist
KEY_PACKAGES=(
    "package.json"
    "server/package.json"
    "frontend/package.json"
    "collector/package.json"
)

TOTAL_PACKAGES=0
MISSING_PACKAGES=0

for pkg in "${KEY_PACKAGES[@]}"; do
    TOTAL_PACKAGES=$((TOTAL_PACKAGES + 1))
    if [ ! -f "$pkg" ]; then
        echo -e "${RED}❌ Missing package.json: $pkg${NC}"
        MISSING_PACKAGES=$((MISSING_PACKAGES + 1))
    else
        echo -e "${GREEN}✅ Found package.json: $pkg${NC}"
    fi
done

echo
echo "📊 Verification Summary"
echo "====================="
echo -e "File Paths:        ${GREEN}$((TOTAL_PATHS - MISSING_PATHS))${NC}/${TOTAL_PATHS} found"
echo -e "LLM Providers:     ${GREEN}$((TOTAL_PROVIDERS - MISSING_PROVIDERS))${NC}/${TOTAL_PROVIDERS} found"
echo -e "Vector DBs:        ${GREEN}$((TOTAL_VECTOR_DBS - MISSING_VECTOR_DBS))${NC}/${TOTAL_VECTOR_DBS} found"
echo -e "Embedding Engines: ${GREEN}$((TOTAL_EMBEDDINGS - MISSING_EMBEDDINGS))${NC}/${TOTAL_EMBEDDINGS} found"
echo -e "Package Files:     ${GREEN}$((TOTAL_PACKAGES - MISSING_PACKAGES))${NC}/${TOTAL_PACKAGES} found"

TOTAL_MISSING=$((MISSING_PATHS + MISSING_PROVIDERS + MISSING_VECTOR_DBS + MISSING_EMBEDDINGS + MISSING_PACKAGES))

echo
if [ $TOTAL_MISSING -eq 0 ]; then
    echo -e "${GREEN}🎉 All checks passed! Feature map is accurate.${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Found $TOTAL_MISSING missing items. Feature map may need updates.${NC}"
    exit 1
fi