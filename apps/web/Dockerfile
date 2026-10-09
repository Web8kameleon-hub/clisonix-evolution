FROM node:20-alpine AS builder

WORKDIR /app

ARG NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY
ARG NEXT_PUBLIC_API_BASE
ARG NEXT_PUBLIC_GOOGLE_ADSENSE_ID
ARG AUTH_SECRET
ARG NEXTAUTH_SECRET

COPY package*.json ./
RUN npm install --legacy-peer-deps

COPY . .

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=$NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY
ENV NEXT_PUBLIC_API_BASE=$NEXT_PUBLIC_API_BASE
ENV NEXT_PUBLIC_GOOGLE_ADSENSE_ID=$NEXT_PUBLIC_GOOGLE_ADSENSE_ID
ENV AUTH_SECRET=$AUTH_SECRET
ENV NEXTAUTH_SECRET=$NEXTAUTH_SECRET

RUN npm run build

# Production image
FROM node:20-alpine AS runner

# Install curl for healthcheck
RUN apk add --no-cache curl

# Install PM2 runtime for graceful cluster reloads
RUN npm install -g pm2

WORKDIR /app

RUN addgroup -g 1001 -S nodejs
RUN adduser -S clisonix -u 1001

COPY --from=builder --chown=clisonix:nodejs /app/.next ./.next
COPY --from=builder --chown=clisonix:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=clisonix:nodejs /app/package*.json ./
COPY --from=builder --chown=clisonix:nodejs /app/public ./public
USER clisonix

EXPOSE 3000

ENV NODE_ENV=production
ENV PORT=3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:3000 || exit 1

CMD ["npm", "start"]
