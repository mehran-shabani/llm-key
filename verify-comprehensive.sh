#!/bin/bash
set -euo pipefail

echo "== Checking declared paths exist =="
paths=(
server/endpoints/chat.js
server/utils/chats/stream.js
frontend/src/components/WorkspaceChat
server/models/workspaceChats.js
server/utils/chats/index.js
server/endpoints/workspaces.js
server/models/workspace.js
server/endpoints/workspaceThreads.js
server/models/workspaceThread.js
collector/processSingleFile
collector/utils/constants.js
collector/processSingleFile/convert/asAudio.js
server/utils/WhisperProviders
collector/processSingleFile/convert/asImage.js
collector/utils/OCRLoader
collector/utils/extensions/WebsiteDepth
collector/processLink
collector/utils/extensions/RepoLoader
collector/utils/extensions/RepoLoader/GithubRepo
collector/utils/extensions/RepoLoader/GitlabRepo
collector/utils/extensions/Confluence
collector/utils/extensions/YoutubeTranscript
collector/utils/extensions/ObsidianVault
server/jobs/sync-watched-documents.js
server/models/documentSyncQueue.js
frontend/src/components/SpeechToText/BrowserNative
server/utils/TextToSpeech
frontend/src/components/TextToSpeech
server/utils/AiProviders
server/utils/files/multer.js
server/utils/MCP
server/endpoints/mcpServers.js
server/utils/vectorDbProviders
server/utils/EmbeddingEngines
server/storage/vector-cache
server/models/vectors.js
server/models/user.js
server/utils/middleware/multiUserProtected.js
server/endpoints/admin.js
server/utils/middleware/simpleSSOEnabled.js
frontend/src/pages/Login/SSO
server/models/apiKeys.js
server/endpoints/api
frontend/src/pages/Admin/Users
frontend/src/pages/Admin/Workspaces
server/models/systemSettings.js
server/models/eventLogs.js
frontend/src/pages/Admin/Logging
server/models/invite.js
frontend/src/pages/Admin/Invitations
server/endpoints/agentWebsocket.js
server/utils/agents/aibitat/plugins/websocket.js
server/utils/agentFlows/executor.js
server/utils/agentFlows/executors
server/endpoints/mobile
server/models/mobileDevice.js
server/endpoints/mobile/index.js
server/endpoints/mobile/utils
server/swagger
server/endpoints/browserExtension.js
server/models/browserExtensionApiKey.js
server/endpoints/embed
server/models/embedConfig.js
server/endpoints/api/openai
server/utils/chats/openaiCompatible.js
docker/Dockerfile
docker/docker-compose.yml
docker/docker-entrypoint.sh
cloud-deployments/aws
cloud-deployments/gcp
cloud-deployments/digitalocean
server/utils/boot
server/prisma
server/storage/models
server/utils/EmbeddingEngines/native
server/utils/agents/imported.js
server/utils/agents/aibitat/plugins
server/models/telemetry.js
server/utils/telemetry
server/utils/logger
docker/docker-healthcheck.sh
)
missing=0
for p in "${paths[@]}"; do
  if [ -e "$p" ]; then
    printf "OK     %s\n" "$p"
  else
    printf "MISSING %s\n" "$p"
    ((missing++)) || true
  fi
done
echo "Missing count: $missing"

echo -e "\n== Checking declared providers/directories =="
echo "AiProviders subdirs:"
fd . server/utils/AiProviders -t d -d 2 || true
echo "Vector DB providers subdirs:"
fd . server/utils/vectorDbProviders -t d -d 2 || true
echo "EmbeddingEngines subdirs:"
fd . server/utils/EmbeddingEngines -t d -d 2 || true

echo -e "\n== Checking dependency claims across package.json =="
deps=( "@mintplex-labs/express-ws" "express-ws" "winston" "posthog" "@ladjs/graceful" "@microsoft/fetch-event-source" "prisma" "bcrypt" "jsonwebtoken" "uuid-apikey" "multer" "react-speech-recognition" "@modelcontextprotocol/sdk" "@xenova/transformers" "mysql2" "pg" "mssql" )
fd package.json -a | while read -r pj; do
  echo ">> $pj"
  for d in "${deps[@]}"; do
    if jq -e --arg d "$d" '.dependencies[$d] or .devDependencies[$d]' "$pj" >/dev/null 2>&1; then
      printf "  dep OK  %s\n" "$d"
    fi
  done
done

echo -e "\n== Searching for MCP/uvx mentions =="
rg -n "modelcontextprotocol|mcp|uvx" -S || true

echo -e "\nDone."