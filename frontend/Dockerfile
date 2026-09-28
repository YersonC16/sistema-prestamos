FROM node:20-alpine AS build

WORKDIR /app

ARG VITE_ASSET_SERVICE_URL
ARG VITE_LOAN_SERVICE_URL
ENV VITE_ASSET_SERVICE_URL=$VITE_ASSET_SERVICE_URL
ENV VITE_LOAN_SERVICE_URL=$VITE_LOAN_SERVICE_URL

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80