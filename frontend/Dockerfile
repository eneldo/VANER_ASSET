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

RUN mkdir -p /var/cache/nginx /var/run +    && touch /var/run/nginx.pid +    && chown -R nginx:nginx /usr/share/nginx/html /var/cache/nginx /var/run /etc/nginx/conf.d

USER nginx

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
