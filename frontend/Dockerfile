# ============================================================
# VANER ASSET - Frontend
# Dockerfile de Producción
# ============================================================

ARG NODE_IMAGE=node:24-alpine3.24
ARG NGINX_IMAGE=nginx:stable-alpine3.24

# ============================================================
# ETAPA 1 - BUILD REACT / VITE
# ============================================================

FROM ${NODE_IMAGE} AS build

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY index.html vite.config.js ./
COPY public ./public
COPY src ./src

ARG VITE_API_URL=/api
ENV VITE_API_URL=${VITE_API_URL}

RUN npm run build


# ============================================================
# ETAPA 2 - NGINX
# ============================================================

FROM ${NGINX_IMAGE}

RUN rm -f /etc/nginx/conf.d/default.conf

COPY --from=build /app/dist /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf

RUN mkdir -p \
        /var/cache/nginx/client_temp \
        /var/cache/nginx/proxy_temp \
        /var/cache/nginx/fastcgi_temp \
        /var/cache/nginx/uwsgi_temp \
        /var/cache/nginx/scgi_temp \
        /run \
    && touch /run/nginx.pid \
    && chown -R nginx:nginx \
        /usr/share/nginx/html \
        /var/cache/nginx \
        /run \
        /etc/nginx/conf.d

USER nginx

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]