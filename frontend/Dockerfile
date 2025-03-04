FROM node:18

WORKDIR /app

COPY package.json yarn.lock ./

RUN yarn set version berry
RUN yarn install 
RUN yarn add axios

COPY . .

EXPOSE 8081

CMD ["yarn", "serve"]