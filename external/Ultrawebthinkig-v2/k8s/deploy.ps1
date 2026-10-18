# EuroWeb AGI Platform - Production Deployment Script (PowerShell)
# Deploy all Kubernetes resources for industrial production

param(
    [switch]$SkipSecrets,
    [switch]$DryRun,
    [string]$Namespace = "euroweb-production"
)

Write-Host "🚀 EuroWeb AGI Platform - Production Deployment" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan

# Check if kubectl is available
try {
    kubectl version --client | Out-Null
    Write-Host "✅ kubectl is available" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: kubectl is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Check if we can connect to cluster
try {
    $clusterCheck = kubectl cluster-info 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  Warning: Cannot connect to Kubernetes cluster" -ForegroundColor Yellow
        Write-Host "   This is normal if no cluster is configured" -ForegroundColor Yellow
        Write-Host "   Configure kubectl with: kubectl config set-cluster ..." -ForegroundColor Yellow
    } else {
        Write-Host "✅ Connected to Kubernetes cluster" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Warning: Cannot connect to Kubernetes cluster" -ForegroundColor Yellow
    Write-Host "   This is normal if no cluster is configured" -ForegroundColor Yellow
}

$currentContext = kubectl config current-context
Write-Host "🔗 Connected to cluster: $currentContext" -ForegroundColor Blue

# Create namespace if it doesn't exist
Write-Host "📁 Creating namespace..." -ForegroundColor Yellow
if ($DryRun) {
    kubectl create namespace $Namespace --dry-run=client -o yaml
} else {
    kubectl create namespace $Namespace --dry-run=client -o yaml | kubectl apply -f -
}

# Apply secrets (user must provide actual secret values)
if (-not $SkipSecrets) {
    Write-Host "🔐 Applying secrets and configuration..." -ForegroundColor Yellow
    if (Test-Path "secrets.yaml") {
        Write-Host "⚠️  Warning: Please ensure secrets.yaml contains actual base64-encoded values" -ForegroundColor Yellow
        $confirmation = Read-Host "Have you updated secrets.yaml with real values? (y/N)"
        if ($confirmation -eq 'y' -or $confirmation -eq 'Y') {
            if ($DryRun) {
                Write-Host "DRY RUN: Would apply secrets.yaml" -ForegroundColor Magenta
            } else {
                kubectl apply -f secrets.yaml
                Write-Host "✅ Secrets applied" -ForegroundColor Green
            }
        } else {
            Write-Host "❌ Skipping secrets - please update secrets.yaml first" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ secrets.yaml not found" -ForegroundColor Red
    }
}

# Apply services
Write-Host "🌐 Applying services..." -ForegroundColor Yellow
if (Test-Path "service.yaml") {
    if ($DryRun) {
        Write-Host "DRY RUN: Would apply service.yaml" -ForegroundColor Magenta
    } else {
        kubectl apply -f service.yaml
        Write-Host "✅ Services applied" -ForegroundColor Green
    }
} else {
    Write-Host "❌ service.yaml not found" -ForegroundColor Red
}

# Apply deployment
Write-Host "🚢 Applying deployment..." -ForegroundColor Yellow
if (Test-Path "production.yaml") {
    if ($DryRun) {
        Write-Host "DRY RUN: Would apply production.yaml" -ForegroundColor Magenta
    } else {
        kubectl apply -f production.yaml
        Write-Host "✅ Deployment applied" -ForegroundColor Green
    }
} else {
    Write-Host "❌ production.yaml not found" -ForegroundColor Red
}

# Apply autoscaler
Write-Host "📈 Applying autoscaler..." -ForegroundColor Yellow
if (Test-Path "autoscaler.yaml") {
    if ($DryRun) {
        Write-Host "DRY RUN: Would apply autoscaler.yaml" -ForegroundColor Magenta
    } else {
        kubectl apply -f autoscaler.yaml
        Write-Host "✅ Autoscaler applied" -ForegroundColor Green
    }
} else {
    Write-Host "❌ autoscaler.yaml not found" -ForegroundColor Red
}

if (-not $DryRun) {
    # Wait for deployment to be ready
    Write-Host "⏳ Waiting for deployment to be ready..." -ForegroundColor Yellow
    kubectl wait --for=condition=available --timeout=300s deployment/euroweb-deployment -n $Namespace

    # Get service info
    Write-Host "`n🌐 Service Information:" -ForegroundColor Blue
    kubectl get services -n $Namespace

    # Get pod status
    Write-Host "`n🐳 Pod Status:" -ForegroundColor Blue
    kubectl get pods -n $Namespace

    # Get HPA status
    Write-Host "`n📊 Autoscaler Status:" -ForegroundColor Blue
    kubectl get hpa -n $Namespace

    # Get external IP (if LoadBalancer)
    Write-Host "`n🔍 Getting external access information..." -ForegroundColor Yellow
    try {
        $externalIP = kubectl get service euroweb-service -n $Namespace -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>$null
        if ($externalIP) {
            Write-Host "🌐 External access: http://$externalIP" -ForegroundColor Green
            Write-Host "🌐 HTTPS access: https://$externalIP" -ForegroundColor Green
        } else {
            Write-Host "⏳ External IP not yet assigned, check with: kubectl get svc -n $Namespace" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⏳ External IP not yet assigned" -ForegroundColor Yellow
    }

    Write-Host "`n🎉 EuroWeb AGI Platform deployment complete!" -ForegroundColor Green
    Write-Host "📊 Monitor with: kubectl get all -n $Namespace" -ForegroundColor Blue
    Write-Host "📋 Logs: kubectl logs -f deployment/euroweb-deployment -n $Namespace" -ForegroundColor Blue
    Write-Host "⚖️  Scale: kubectl scale deployment euroweb-deployment --replicas=5 -n $Namespace" -ForegroundColor Blue
} else {
    Write-Host "`n✅ Dry run completed - no resources were actually applied" -ForegroundColor Green
    Write-Host "Run without -DryRun to actually deploy" -ForegroundColor Blue
}

# Usage examples
Write-Host "`n📖 Usage Examples:" -ForegroundColor Cyan
Write-Host "  ./deploy.ps1                    # Full deployment with prompts" -ForegroundColor White
Write-Host "  ./deploy.ps1 -SkipSecrets       # Skip secrets application" -ForegroundColor White
Write-Host "  ./deploy.ps1 -DryRun           # Preview what would be deployed" -ForegroundColor White
Write-Host "  ./deploy.ps1 -Namespace staging # Deploy to staging namespace" -ForegroundColor White
