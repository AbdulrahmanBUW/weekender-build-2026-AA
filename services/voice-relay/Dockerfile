# voice-relay container (Render / Fly.io / local Docker). See docs/deploy-relay.md.
# Secrets (DEEPGRAM_API_KEY, SUPABASE_SERVICE_ROLE_KEY) are NEVER baked in: .env is excluded by
# .dockerignore; pass them at runtime (--env-file locally, dashboard/secrets on Render/Fly).
FROM node:22-alpine

ENV NODE_ENV=production \
    PORT=8787 \
    # Bind address. server.js must read it: server.listen(PORT, process.env.HOST || '127.0.0.1', ...)
    # Without that change the relay binds 127.0.0.1 inside the container and is unreachable from outside.
    HOST=0.0.0.0

WORKDIR /app

# Install prod deps first (cached layer as long as the lockfile does not change).
COPY package.json package-lock.json ./
RUN npm ci --omit=dev && npm cache clean --force

# App code (test/probe scripts, .env, audio files are filtered by .dockerignore).
COPY --chown=node:node . .

# Non-root: the official image ships a "node" user (uid 1000).
USER node

EXPOSE 8787

# Local Docker only (Render and Fly use their own HTTP check on /health). Runs inside the container,
# so it works with either bind address.
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD wget -qO- "http://127.0.0.1:${PORT}/health" >/dev/null || exit 1

CMD ["node", "server.js"]
