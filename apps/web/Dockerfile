# apps/web/Dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json pnpm-lock.yaml* ./
RUN npm install -g pnpm && pnpm install --no-frozen-lockfile
COPY . .
RUN pnpm build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 8080
ENV PORT=8080
RUN sed -i "s/listen\s\+80;/listen ${PORT};/" /etc/nginx/conf.d/default.conf

CMD ["nginx", "-g", "daemon off;"]
