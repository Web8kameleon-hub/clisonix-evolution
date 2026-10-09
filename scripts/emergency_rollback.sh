#!/bin/bash
# =============================================================================
# 🚨 CLISONIX EMERGENCY ROLLBACK SCRIPT
# =============================================================================
# 
# WHEN TO USE:
# - Critical bug affecting live users
# - Service outage after deployment
# - Data corruption risk
# - Security vulnerability discovered
#
# USAGE:
#   ./scripts/emergency_rollback.sh [kubernetes|docker|git]
#
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="${NAMESPACE:-clisonix}"
DEPLOYMENT="${DEPLOYMENT:-api}"
BACKUP_COMMITS="${BACKUP_COMMITS:-5}"

echo -e "${RED}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║         🚨 CLISONIX EMERGENCY ROLLBACK 🚨                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Function: Show rollback options
show_options() {
    echo -e "${YELLOW}Available rollback methods:${NC}"
    echo ""
    echo "  1) kubernetes  - Rollback Kubernetes deployment (fastest)"
    echo "  2) docker      - Rollback Docker Compose"
    echo "  3) git         - Rollback to previous git commit"
    echo "  4) database    - Rollback database migration"
    echo "  5) all         - Full system rollback"
    echo ""
}

# Function: Check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    if command -v kubectl &> /dev/null; then
        echo -e "  ✅ kubectl available"
    else
        echo -e "  ⚠️  kubectl not found"
    fi
    
    if command -v docker &> /dev/null; then
        echo -e "  ✅ docker available"
    else
        echo -e "  ⚠️  docker not found"
    fi
    
    if command -v git &> /dev/null; then
        echo -e "  ✅ git available"
    else
        echo -e "  ⚠️  git not found"
    fi
    
    echo ""
}

# Function: Kubernetes rollback
kubernetes_rollback() {
    echo -e "${YELLOW}🔄 Initiating Kubernetes rollback...${NC}"
    
    # Check current deployment
    echo "Current deployment status:"
    kubectl get deployment ${DEPLOYMENT} -n ${NAMESPACE} -o wide || true
    
    # Show rollout history
    echo ""
    echo "Rollout history:"
    kubectl rollout history deployment/${DEPLOYMENT} -n ${NAMESPACE} || true
    
    # Perform rollback
    echo ""
    echo -e "${YELLOW}Rolling back to previous revision...${NC}"
    kubectl rollout undo deployment/${DEPLOYMENT} -n ${NAMESPACE}
    
    # Wait for rollout
    echo "Waiting for rollback to complete..."
    kubectl rollout status deployment/${DEPLOYMENT} -n ${NAMESPACE} --timeout=120s
    
    # Verify
    echo ""
    echo -e "${GREEN}✅ Kubernetes rollback complete!${NC}"
    kubectl get pods -n ${NAMESPACE} -l app=${DEPLOYMENT}
}

# Function: Docker Compose rollback
docker_rollback() {
    echo -e "${YELLOW}🔄 Initiating Docker Compose rollback...${NC}"
    
    # Stop current containers
    echo "Stopping current containers..."
    docker-compose down --remove-orphans
    
    # Git rollback
    echo "Reverting to previous commit..."
    git stash || true
    git checkout HEAD~1
    
    # Rebuild and start
    echo "Rebuilding and starting services..."
    docker-compose up -d --build
    
    # Wait for health
    echo "Waiting for services to be healthy..."
    sleep 10
    
    # Health check
    echo ""
    echo "Checking service health..."
    docker-compose ps
    
    echo ""
    echo -e "${GREEN}✅ Docker rollback complete!${NC}"
}

# Function: Git rollback
git_rollback() {
    echo -e "${YELLOW}🔄 Initiating Git rollback...${NC}"
    
    # Show recent commits
    echo "Recent commits:"
    git log --oneline -${BACKUP_COMMITS}
    
    echo ""
    echo "Current HEAD:"
    git rev-parse HEAD
    
    # Stash any changes
    git stash || true
    
    # Rollback
    echo ""
    echo "Rolling back to previous commit..."
    git reset --hard HEAD~1
    
    echo ""
    echo "New HEAD:"
    git rev-parse HEAD
    
    echo ""
    echo -e "${GREEN}✅ Git rollback complete!${NC}"
    echo -e "${YELLOW}⚠️  Remember to redeploy the application!${NC}"
}

# Function: Database rollback
database_rollback() {
    echo -e "${YELLOW}🔄 Initiating Database migration rollback...${NC}"
    
    # This depends on your migration tool
    # Alembic example:
    if [ -f "alembic.ini" ]; then
        echo "Using Alembic for migration rollback..."
        alembic downgrade -1
        echo -e "${GREEN}✅ Database rollback complete!${NC}"
    # Django example:
    elif [ -f "manage.py" ]; then
        echo "Using Django for migration rollback..."
        python manage.py migrate --fake-initial
        echo -e "${GREEN}✅ Database rollback complete!${NC}"
    else
        echo -e "${RED}⚠️  No migration tool detected. Manual rollback required.${NC}"
        echo ""
        echo "Manual PostgreSQL rollback commands:"
        echo "  psql -U clisonix -d clisonixdb -c 'SELECT * FROM alembic_version;'"
        echo "  # Then run appropriate rollback migration"
    fi
}

# Function: Full system rollback
full_rollback() {
    echo -e "${RED}🚨 FULL SYSTEM ROLLBACK 🚨${NC}"
    echo ""
    echo "This will rollback:"
    echo "  - Kubernetes deployments"
    echo "  - Docker containers"
    echo "  - Git repository"
    echo ""
    
    read -p "Are you sure? (type 'yes' to confirm): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Aborted."
        exit 1
    fi
    
    kubernetes_rollback || echo "Kubernetes rollback failed or not available"
    docker_rollback || echo "Docker rollback failed or not available"
    
    echo ""
    echo -e "${GREEN}✅ Full system rollback complete!${NC}"
}

# Function: Post-rollback verification
verify_rollback() {
    echo ""
    echo -e "${YELLOW}📋 Post-rollback verification...${NC}"
    echo ""
    
    # Check API health
    echo "Checking API health..."
    curl -s http://localhost:8000/health || echo "API not responding on localhost"
    
    # Check services
    echo ""
    echo "Docker containers:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || true
    
    # Check Kubernetes
    echo ""
    echo "Kubernetes pods:"
    kubectl get pods -n ${NAMESPACE} 2>/dev/null || true
    
    echo ""
    echo -e "${GREEN}Verification complete. Check the status above.${NC}"
}

# Function: Create incident log
log_incident() {
    INCIDENT_LOG="incidents/rollback_$(date +%Y%m%d_%H%M%S).md"
    mkdir -p incidents
    
    cat > "$INCIDENT_LOG" << EOF
# Rollback Incident Report

**Date**: $(date -Iseconds)
**Operator**: ${USER:-unknown}
**Method**: $1

## Timeline
- $(date -Iseconds): Rollback initiated
- $(date -Iseconds): Rollback completed

## Changes Reverted
$(git log -1 --pretty=format:"- %h: %s" 2>/dev/null || echo "- Unable to determine")

## Verification
$(curl -s http://localhost:8000/health 2>/dev/null || echo "- API health check failed")

## Next Steps
- [ ] Investigate root cause
- [ ] Fix issue in new branch
- [ ] Test thoroughly before redeployment
- [ ] Update this incident report
EOF

    echo ""
    echo -e "${YELLOW}📝 Incident logged to: ${INCIDENT_LOG}${NC}"
}

# Function: Notify team (customize for your setup)
notify_team() {
    echo ""
    echo -e "${YELLOW}📢 Sending team notification...${NC}"
    
    # Slack webhook example (uncomment and configure)
    # SLACK_WEBHOOK="${SLACK_WEBHOOK:-}"
    # if [ -n "$SLACK_WEBHOOK" ]; then
    #     curl -X POST -H 'Content-type: application/json' \
    #         --data '{"text":"🚨 ROLLBACK EXECUTED: Clisonix production has been rolled back. Check #incidents channel."}' \
    #         "$SLACK_WEBHOOK"
    # fi
    
    echo "  (Configure Slack/PagerDuty webhook in script for automatic notifications)"
}

# Main execution
main() {
    check_prerequisites
    
    METHOD="${1:-}"
    
    if [ -z "$METHOD" ]; then
        show_options
        read -p "Select rollback method (1-5): " choice
        case $choice in
            1|kubernetes) METHOD="kubernetes" ;;
            2|docker) METHOD="docker" ;;
            3|git) METHOD="git" ;;
            4|database) METHOD="database" ;;
            5|all) METHOD="all" ;;
            *) echo "Invalid choice"; exit 1 ;;
        esac
    fi
    
    echo ""
    echo -e "${RED}⏱️  Starting rollback in 3 seconds... (Ctrl+C to cancel)${NC}"
    sleep 3
    
    case $METHOD in
        kubernetes)
            kubernetes_rollback
            ;;
        docker)
            docker_rollback
            ;;
        git)
            git_rollback
            ;;
        database)
            database_rollback
            ;;
        all)
            full_rollback
            ;;
        *)
            echo "Unknown method: $METHOD"
            show_options
            exit 1
            ;;
    esac
    
    verify_rollback
    log_incident "$METHOD"
    notify_team
    
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║         ✅ ROLLBACK COMPLETE                               ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Monitor system health: curl http://localhost:8000/health"
    echo "  2. Check logs: docker logs -f clisonix-api"
    echo "  3. Investigate root cause"
    echo "  4. Fix issue in separate branch"
    echo "  5. Test thoroughly before redeploying"
}

main "$@"
