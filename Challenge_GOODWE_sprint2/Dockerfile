FROM node:24-bookworm-slim
WORKDIR /app
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN npx --yes pnpm@11.25.0 install --frozen-lockfile
COPY . .
RUN node node_modules/vite/bin/vite.js build
ENV HOST=0.0.0.0 PORT=3000
EXPOSE 3000
CMD ["node", "server/index.mjs"]
