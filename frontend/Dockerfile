# Stage 0, "build-stage", based on Node, to build and compile the frontend
FROM node:22-alpine AS build-stage

WORKDIR /app

RUN corepack enable && corepack prepare pnpm@latest --activate

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml /app/

COPY frontend/package.json /app/frontend/

WORKDIR /app/frontend

RUN pnpm install --frozen-lockfile

COPY ./frontend /app/frontend
ARG VITE_API_URL

RUN pnpm run build


# Stage 1, based on Nginx, to have only the compiled app, ready for production with Nginx
FROM nginx:1

COPY --from=build-stage /app/frontend/dist/ /usr/share/nginx/html

COPY ./frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY ./frontend/nginx-backend-not-found.conf /etc/nginx/extra-conf.d/backend-not-found.conf