FROM node:22.23.1-bookworm-slim AS dependencies
ENV PNPM_HOME=/pnpm
ENV PATH="${PNPM_HOME}:${PATH}"
WORKDIR /app
RUN corepack enable && corepack prepare pnpm@11.20.0 --activate
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY apps/web/package.json apps/web/package.json
RUN pnpm install --frozen-lockfile --filter @growthpilot/web...

FROM dependencies AS builder
COPY apps/web apps/web
RUN pnpm --dir apps/web build

FROM node:22.23.1-bookworm-slim AS runtime
ENV NODE_ENV=production \
    HOSTNAME=0.0.0.0 \
    PORT=3000
WORKDIR /app
RUN groupadd --system growthpilot && useradd --system --gid growthpilot growthpilot
COPY --from=builder --chown=growthpilot:growthpilot /app/apps/web/.next/standalone ./
COPY --from=builder --chown=growthpilot:growthpilot /app/apps/web/.next/static ./apps/web/.next/static
USER growthpilot
EXPOSE 3000
CMD ["node", "apps/web/server.js"]
