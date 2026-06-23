# Story 4.3: Production Deployment

## Story Details
**Epic**: Epic 4 - Enterprise & Scale  
**Story Points**: 8  
**Priority**: P1 (High)  
**Assignee**: DevOps + Backend Developer  
**Sprint**: Week 15

## User Story
**As a** DevOps engineer  
**I want** production-ready deployment infrastructure  
**So that** the MCP server runs reliably at scale with monitoring and auto-scaling

## Acceptance Criteria
- [ ] Docker container builds successfully
- [ ] docker-compose configuration for local development
- [ ] Kubernetes manifests for production
- [ ] Cloud deployment working (AWS/GCP/Azure)
- [ ] Auto-scaling configured (horizontal pod autoscaler)
- [ ] Monitoring and alerting functional
- [ ] CI/CD pipeline operational
- [ ] Health checks and readiness probes
- [ ] Logging aggregation configured
- [ ] Uptime >99.5% target met

## Technical Details

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY templates/ ./templates/

# Create output directory
RUN mkdir -p /app/output

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run server
CMD ["python", "src/mcp/server.py"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  tableau-mcp:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - LOG_LEVEL=INFO
    volumes:
      - ./templates:/app/templates:ro
      - ./output:/app/output
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
```

### Kubernetes Manifests

**Deployment**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tableau-mcp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: tableau-mcp
  template:
    metadata:
      labels:
        app: tableau-mcp
    spec:
      containers:
      - name: tableau-mcp
        image: tableau-mcp:latest
        ports:
        - containerPort: 8000
        env:
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: tableau-secrets
              key: gemini-api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

**Service**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: tableau-mcp-service
spec:
  selector:
    app: tableau-mcp
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

**HorizontalPodAutoscaler**:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: tableau-mcp-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: tableau-mcp
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### CI/CD Pipeline (GitHub Actions)
```yaml
name: Build and Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    - name: Run tests
      run: pytest tests/ --cov=src --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Build Docker image
      run: docker build -t tableau-mcp:${{ github.sha }} .
    - name: Push to registry
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker push tableau-mcp:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/tableau-mcp tableau-mcp=tableau-mcp:${{ github.sha }}
        kubectl rollout status deployment/tableau-mcp
```

### Monitoring Stack
- **Prometheus**: Metrics collection
- **Grafana**: Visualization dashboards
- **Loki**: Log aggregation
- **AlertManager**: Alert routing

## Implementation Tasks
- [ ] Create Dockerfile
- [ ] Write docker-compose.yml
- [ ] Build Docker image and test locally
- [ ] Push image to container registry
- [ ] Create Kubernetes deployment manifests
- [ ] Create Kubernetes service manifests
- [ ] Configure HorizontalPodAutoscaler
- [ ] Set up CI/CD pipeline (GitHub Actions)
- [ ] Configure secrets management
- [ ] Deploy to staging environment
- [ ] Load testing (100+ concurrent users)
- [ ] Set up Prometheus monitoring
- [ ] Create Grafana dashboards
- [ ] Configure Loki for logging
- [ ] Set up AlertManager rules
- [ ] Deploy to production
- [ ] Monitor uptime and performance

## Testing Strategy
- Local Docker testing
- Staging environment validation
- Load testing (Apache Bench, Locust)
- Chaos engineering (kill pods, simulate failures)
- Monitor metrics during testing
- Verify auto-scaling behavior
- Test rollback procedures

## Documentation
- Docker setup guide
- Kubernetes deployment guide
- CI/CD pipeline documentation
- Monitoring and alerting guide
- Incident response playbook
- Scaling and performance tuning
- Cost optimization guide

## Definition of Done
- [ ] Docker container working
- [ ] Kubernetes deployment successful
- [ ] Auto-scaling functional
- [ ] CI/CD pipeline operational
- [ ] Monitoring and alerting configured
- [ ] Load testing passed (100+ users)
- [ ] Uptime >99.5% achieved
- [ ] Documentation complete
- [ ] Code and infrastructure reviewed

## Related Stories
- **Depends On**: All previous stories (complete system required)
- **Blocks**: Story 4.4 (Launch)

## Notes
- Choose cloud provider based on existing infrastructure
- Consider managed Kubernetes (EKS, GKE, AKS) for easier operations
- Estimate costs: ~$200-500/month for small production deployment
- Security: API keys in Kubernetes Secrets, not environment variables
- Consider adding CDN for static assets (templates, previews)
- Implement rate limiting to prevent abuse
- Add request queueing for high load scenarios

