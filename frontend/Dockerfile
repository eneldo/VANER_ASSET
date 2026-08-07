# =========================================================
# FRONTEND BUILD
# =========================================================

ARG NODE_IMAGE=node:24.15.0-alpine3.22
ARG NGINX_IMAGE=nginx:1.28.0-alpine
FROM ${NODE_IMAGE} AS build

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY index.html vite.config.js ./
COPY public ./public
COPY src ./src

ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# =========================================================
# NGINX PRODUCCIÓN
# =========================================================

FROM ${NGINX_IMAGE}

RUN apk upgrade --no-cache

COPY --from=build /app/dist /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
