# Multi-stage build for ResoftAI Frontend
FROM node:18-alpine as builder

# Set working directory
WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY frontend/ .

# Build for production
RUN npm run build

# ===== Production Stage with Nginx =====
FROM nginx:alpine

# Copy custom nginx config
COPY docker/frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Copy built files from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Add healthcheck
RUN apk add --no-cache curl

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
