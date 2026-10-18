# EuroWeb AGI Platform - Kubernetes Deployment

## 🚀 Production-Ready Kubernetes Configuration

This directory contains all the necessary Kubernetes manifests to deploy the EuroWeb AGI Platform to production.

### 📁 Files Overview

| File | Purpose | Description |
|------|---------|-------------|
| `production.yaml` | Main Deployment | Primary application deployment with AGI sidecar |
| `service.yaml` | Network Services | LoadBalancer, ClusterIP, and Headless services |
| `secrets.yaml` | Security Config | Secrets, ConfigMap, and NetworkPolicy |
| `autoscaler.yaml` | Scaling Config | HPA, VPA, and PodDisruptionBudget |
| `deploy.ps1` | PowerShell Deploy | Windows deployment script |
| `deploy.sh` | Bash Deploy | Linux/macOS deployment script |

## 🛠️ Prerequisites

### Required Tools

- `kubectl` configured with access to your cluster
- Kubernetes cluster (AWS EKS, GKE, AKS, or on-premises)
- AWS Load Balancer Controller (for AWS EKS)

### Required Secrets

Before deployment, update `secrets.yaml` with base64-encoded values:

```bash
# Encode secrets (replace with actual values)
echo -n "your-claude-api-key" | base64
echo -n "your-openai-api-key" | base64
echo -n "your-supabase-url" | base64
```

## 🚀 Quick Deployment

### Windows (PowerShell)

```powershell
# Preview deployment
.\k8s\deploy.ps1 -DryRun

# Full deployment
.\k8s\deploy.ps1

# Skip secrets if already configured
.\k8s\deploy.ps1 -SkipSecrets
```

### Linux/macOS (Bash)

```bash
# Make executable
chmod +x k8s/deploy.sh

# Deploy
./k8s/deploy.sh
```

## 📋 Manual Deployment Steps

If you prefer manual deployment:

```bash
# 1. Create namespace
kubectl create namespace euroweb-production

# 2. Apply secrets (update with real values first!)
kubectl apply -f k8s/secrets.yaml

# 3. Apply services
kubectl apply -f k8s/service.yaml

# 4. Apply deployment
kubectl apply -f k8s/production.yaml

# 5. Apply autoscaling
kubectl apply -f k8s/autoscaler.yaml
```

## 🔧 Configuration Details

### Deployment Specifications

- **Replicas**: 3 (minimum for high availability)
- **Resource Requests**: 1 CPU, 2Gi RAM per pod
- **Resource Limits**: 2 CPU, 4Gi RAM per pod
- **Readiness/Liveness Probes**: Configured for health monitoring

### Service Configuration

- **LoadBalancer**: External access via AWS NLB
- **ClusterIP**: Internal cluster communication
- **Headless**: For StatefulSet scenarios

### Autoscaling

- **HPA**: CPU (70%) and Memory (80%) based scaling
- **Min Replicas**: 3
- **Max Replicas**: 20
- **VPA**: Automatic resource optimization

## 🌐 Network Configuration

### Ports

- **3000**: Main web application
- **8080**: AGI services
- **9100**: Metrics/monitoring

### Security

- NetworkPolicy restricts pod-to-pod communication
- Secrets stored securely in Kubernetes
- Non-root container execution

## 📊 Monitoring & Scaling

### Check Status

```bash
# Overall status
kubectl get all -n euroweb-production

# Pod details
kubectl describe pods -n euroweb-production

# Service endpoints
kubectl get endpoints -n euroweb-production

# Autoscaler status
kubectl get hpa -n euroweb-production
```

### Manual Scaling

```bash
# Scale deployment
kubectl scale deployment euroweb-deployment --replicas=5 -n euroweb-production

# Update resources
kubectl patch deployment euroweb-deployment -n euroweb-production -p '{"spec":{"template":{"spec":{"containers":[{"name":"euroweb-app","resources":{"requests":{"cpu":"2000m","memory":"4Gi"}}}]}}}}'
```

### Logs

```bash
# Application logs
kubectl logs -f deployment/euroweb-deployment -n euroweb-production

# AGI sidecar logs
kubectl logs -f deployment/euroweb-deployment -c agi-sidecar -n euroweb-production

# Previous pod logs
kubectl logs deployment/euroweb-deployment --previous -n euroweb-production
```

## 🔐 Security Considerations

### Secrets Management

- Use external secret management (AWS Secrets Manager, Vault, etc.)
- Rotate secrets regularly
- Never commit actual secrets to git

### Network Security

- NetworkPolicy limits ingress/egress
- Use TLS termination at load balancer
- Consider service mesh (Istio) for advanced security

### RBAC

Create service account with minimal permissions:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: euroweb-sa
  namespace: euroweb-production
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: euroweb-role
  namespace: euroweb-production
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["get", "list"]
```

## 🚨 Troubleshooting

### Common Issues

1. **Pods not starting**

   ```bash
   kubectl describe pod <pod-name> -n euroweb-production
   kubectl logs <pod-name> -n euroweb-production
   ```

2. **Service not accessible**

   ```bash
   kubectl get svc -n euroweb-production
   kubectl describe svc euroweb-service -n euroweb-production
   ```

3. **LoadBalancer pending**
   - Check AWS Load Balancer Controller is installed
   - Verify IAM permissions
   - Check VPC/subnet configuration

### Health Checks

- Application: `http://<pod-ip>:3000/api/health`
- AGI Service: `http://<pod-ip>:8080/health`
- Metrics: `http://<pod-ip>:9100/metrics`

## 🔄 Updates & Rollbacks

### Rolling Updates

```bash
# Update image
kubectl set image deployment/euroweb-deployment euroweb-app=ghcr.io/your-org/euroweb-platform:v2.0.0 -n euroweb-production

# Check rollout status
kubectl rollout status deployment/euroweb-deployment -n euroweb-production
```

### Rollbacks

```bash
# Rollback to previous version
kubectl rollout undo deployment/euroweb-deployment -n euroweb-production

# Rollback to specific revision
kubectl rollout undo deployment/euroweb-deployment --to-revision=2 -n euroweb-production
```

## 📈 Performance Tuning

### Resource Optimization

- Monitor actual usage with `kubectl top pods`
- Adjust requests/limits based on metrics
- Use VPA recommendations

### Database Connections

- Configure connection pooling
- Set appropriate timeouts
- Monitor connection metrics

### Caching

- Enable Redis for session storage
- Use CDN for static assets
- Implement application-level caching

---

**🎯
Production Checklist**

- [ ] Secrets updated with real values
- [ ] Load balancer controller installed
- [ ] Monitoring configured (Prometheus/Grafana)
- [ ] Backup strategy in place
- [ ] DNS configured for external access
- [ ] SSL/TLS certificates configured
- [ ] Logging aggregation setup (ELK/Loki)
- [ ] Alerting rules configured
