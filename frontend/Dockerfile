# frontend/Dockerfile
# 빌드

FROM node:20-alpine AS builder

WORKDIR /app

#의존성 먼저
COPY package*.json ./
RUN npm ci

# 빌드 타임 환경변수 넣기
ARG VITE_API_URL 
ENV VITE_API_URL=$VITE_API_URL  

COPY . .
RUN npm run build

# 서빙
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default/conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
