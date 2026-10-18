FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* yarn.lock* ./
RUN npm install

COPY tsconfig.json ./
COPY backend ./backend

ENV NODE_ENV=production
ENV PORT_BACKEND=8080
ENV BACKEND_HOST=0.0.0.0

EXPOSE 8080

CMD ["npx", "tsx", "backend/server.ts"]
