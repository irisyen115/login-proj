FROM node:16

WORKDIR /app


COPY package.json yarn.lock ./

RUN yarn add -D @vue/cli-plugin-unit-jest
RUN yarn install

COPY . .
