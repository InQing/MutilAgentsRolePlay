FROM node:22-alpine AS deps

WORKDIR /app

COPY package.json package-lock.json ./
COPY apps/web/package.json apps/web/package.json
COPY packages/shared-contracts/package.json packages/shared-contracts/package.json

RUN npm ci


FROM node:22-alpine AS builder

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY package.json package-lock.json tsconfig.base.json ./
COPY apps/web ./apps/web
COPY packages/shared-contracts ./packages/shared-contracts

RUN npm run build:web


FROM node:22-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

COPY package.json package-lock.json ./
COPY apps/web/package.json apps/web/package.json
COPY packages/shared-contracts/package.json packages/shared-contracts/package.json

RUN npm ci --omit=dev

COPY tsconfig.base.json ./
COPY apps/web ./apps/web
COPY packages/shared-contracts ./packages/shared-contracts
COPY --from=builder /app/apps/web/.next ./apps/web/.next

EXPOSE 3000

CMD ["./node_modules/.bin/next", "start", "apps/web", "--hostname", "0.0.0.0", "--port", "3000"]
