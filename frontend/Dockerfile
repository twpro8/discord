FROM node:22-alpine AS builder
WORKDIR /app

RUN corepack enable && corepack prepare pnpm@9.15.0 --activate

COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY frontend/ ./

ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_BASE_URL=$VITE_API_URL

RUN pnpm build

FROM node:22-alpine
WORKDIR /app

RUN corepack enable && corepack prepare pnpm@9.15.0 --activate

COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist

EXPOSE 80
CMD ["pnpm", "vite", "preview", "--host", "0.0.0.0", "--port", "80"]
