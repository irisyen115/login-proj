FROM node:18

WORKDIR /app

RUN corepack enable && corepack prepare yarn@3.5.1 --activate

# 複製整個 monorepo（注意這點！）
COPY . .

# 安裝所有工作區依賴
RUN yarn install

# 切換到 login-page 子目錄
WORKDIR /app/packages/login-page

CMD ["yarn", "serve", "--port", "8081"]
