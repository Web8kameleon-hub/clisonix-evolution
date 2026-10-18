# 🚀 EuroWeb Platform - Deployment Guide

## Quick Deployment Options

### 1. Vercel (Recommended)
```bash
# Install Vercel CLI (if not installed)
yarn global add vercel

# Deploy using our script
yarn deploy:vercel

# Or manually
vercel --prod
```

### 2. Docker
```bash
# Build and run with Docker
yarn deploy:docker

# Or manually
yarn docker:build
yarn docker:run

# View logs
yarn docker:logs
```

### 3. Docker Compose (Full Stack)
```bash
# Start all services
yarn deploy:compose

# Stop all services
yarn compose:down

# View logs
yarn compose:logs
```

### 4. Git Deployment
```bash
# Commit and push changes
yarn deploy:git

# Or with custom message
powershell -File scripts/deploy.ps1 -Target git -CommitMessage "Your custom message"
```

## 🛠️ Development Workflow

1. **Start Development**
   ```bash
   yarn dev
   ```

2. **Test Your Changes**
   ```bash
   yarn test
   yarn type-check
   yarn lint
   ```

3. **Build for Production**
   ```bash
   yarn build
   ```

4. **Deploy**
   ```bash
   yarn deploy:vercel
   ```

## 📋 Available Scripts

### Development
- `yarn dev` - Start development server
- `yarn dev:full` - Start app + backend
- `yarn test` - Run tests
- `yarn lint` - Fix linting issues

### Deployment
- `yarn deploy` - Deploy to Vercel (default)
- `yarn deploy:vercel` - Deploy to Vercel
- `yarn deploy:docker` - Build and run Docker container
- `yarn deploy:compose` - Start with Docker Compose
- `yarn deploy:git` - Commit and push to Git

### Docker
- `yarn docker:build` - Build Docker image
- `yarn docker:run` - Run Docker container
- `yarn docker:stop` - Stop and remove container
- `yarn docker:logs` - View container logs

### Docker Compose
- `yarn compose:up` - Start all services
- `yarn compose:down` - Stop all services
- `yarn compose:logs` - View all logs

## 🔧 Postman Collections

Import the following files into Postman:
- `postman/EuroWeb-API.postman_collection.json` - API endpoints
- `postman/Local.postman_environment.json` - Local environment
- `postman/Production.postman_environment.json` - Production environment

## 🌐 URLs

### Local Development
- Application: http://localhost:3000
- Backend API: http://localhost:3001

### Production
- Main Site: https://euroweb.ai
- API: https://api.euroweb.ai
- Admin: https://admin.euroweb.ai

## 📦 Environment Variables

Create `.env.local` for local development:
```env
NODE_ENV=development
NEXT_TELEMETRY_DISABLED=1
# Add other environment variables as needed
```

## 🛡️ Security Notes

- All sensitive data is excluded from git via `.gitignore`
- Docker images use non-root users
- Security headers are configured in `vercel.json`
- HTTPS is enforced in production

## 🔍 Troubleshooting

### Build Issues
```bash
# Clean and rebuild
yarn clean:all
yarn build
```

### Docker Issues
```bash
# Remove all containers and rebuild
yarn docker:stop
yarn docker:build
yarn docker:run
```

### Vercel Issues
```bash
# Re-login and redeploy
vercel login
vercel --prod
```

---

**Author:** Ledjan Ahmati (100% Owner)  
**Contact:** dealsjona@gmail.com  
**Version:** 8.0.0 Ultra
