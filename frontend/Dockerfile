# ---------- build stage ----------
FROM node:22-slim AS builder

ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable && corepack prepare pnpm@10.0.0 --activate

WORKDIR /app

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .
RUN pnpm build

# ---------- serve stage ----------
FROM nginx:1.27-alpine

# Remove default site
RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/templates/default.conf.template
COPY --from=builder /app/dist /usr/share/nginx/html

# Cloud Run injects PORT; nginx template engine substitutes ${PORT}
ENV PORT=8080
ENV BACKEND_URL=http://localhost:8010

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
