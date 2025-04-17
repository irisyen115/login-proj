FROM node:18

WORKDIR /app

COPY src/.yarnrc.yml ./
COPY src/.yarn .yarn
COPY package.json yarn.lock ./

RUN yarn set version berry
RUN corepack enable && yarn install

COPY . .

EXPOSE 8081

CMD ["yarn", "serve", "--port", "8081"]
