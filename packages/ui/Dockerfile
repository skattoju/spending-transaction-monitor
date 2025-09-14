# Multi-stage build for React application using pnpm workspace
FROM node:20-alpine AS builder

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy workspace configuration files
COPY pnpm-workspace.yaml pnpm-lock.yaml package.json ./

# Copy all packages for workspace resolution
COPY packages/ ./packages/

# Install dependencies using pnpm workspace
RUN pnpm install --frozen-lockfile

# Build the UI using workspace filter (skip TypeScript compilation for Docker)
RUN pnpm --filter @spending-monitor/ui exec vite build

# Production stage - use Node.js to serve static files
FROM node:20-alpine

WORKDIR /app

# Install serve package globally to serve static files
RUN npm install -g serve

# Copy built assets
COPY --from=builder /app/packages/ui/dist ./dist

# Create non-root user for OpenShift compatibility
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001 -G nodejs

# Change ownership of the app directory
RUN chown -R nodejs:nodejs /app

# Switch to non-root user
USER nodejs

EXPOSE 8080

# Use serve to host the SPA with proper routing
CMD ["serve", "-s", "dist", "-l", "8080"]