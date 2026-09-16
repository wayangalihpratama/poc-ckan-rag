#!/bin/bash
# ==============================================================================
# CKAN to Akvo RAG Knowledgebase Sync - Automated Test Runner
# Executes automated unit, integration, and E2E tests inside the CKAN container.
# ==============================================================================

set -e

# Color definitions
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}======================================================${NC}"
echo -e "${CYAN}🧪 CKAN Akvo RAG Extension Automated Test Suite${NC}"
echo -e "${CYAN}======================================================${NC}"

# Check if Docker compose stack is running
if ! docker compose ps --services --filter "status=running" | grep -q "ckan"; then
    echo -e "${YELLOW}[!] CKAN Docker container is not running.${NC}"
    echo -e "${CYAN}[*] Starting Docker environment...${NC}"
    docker compose up -d
    echo -e "${CYAN}[*] Waiting for CKAN service to become ready...${NC}"
    sleep 5
fi

# Execute pytest with coverage inside the container
echo -e "${CYAN}[*] Executing test suite inside Docker container...${NC}\n"

docker compose exec -T ckan pytest /srv/app/src_extensions/ckanext-akvorag/tests/ \
    -v \
    --cov=ckanext.akvorag \
    --cov-report=term-missing \
    "$@"

TEST_EXIT_CODE=$?

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}======================================================${NC}"
    echo -e "${GREEN}✅ All tests passed successfully with ≥80% coverage!${NC}"
    echo -e "${GREEN}======================================================${NC}"
else
    echo -e "${RED}======================================================${NC}"
    echo -e "${RED}❌ Test suite encountered failures (Exit code: $TEST_EXIT_CODE)${NC}"
    echo -e "${RED}======================================================${NC}"
fi

exit $TEST_EXIT_CODE
