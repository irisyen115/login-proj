# 使用 Node.js 18 作為基底映像
FROM node:18

# 設定工作目錄
WORKDIR /app

# 複製 package.json 和 yarn.lock 以安裝依賴
COPY package.json yarn.lock ./

# 安裝專案依賴
RUN yarn set version berry
RUN yarn install 

# 複製專案程式碼到容器內
COPY . .

EXPOSE 8081

# 啟動開發伺服器
CMD ["yarn", "serve"]