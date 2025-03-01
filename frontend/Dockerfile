# 使用 Node.js 18 作為基底映像
FROM node:18

# 設定工作目錄
WORKDIR /fronted

# 複製 package.json 和 yarn.lock 以安裝依賴
COPY fronted/package*.json fronted/yarn.lock ./

# 安裝專案依賴
RUN yarn install

# 複製專案程式碼到容器內
COPY fronted .

# 開放 8080 端口
EXPOSE 8081

# 啟動開發伺服器
CMD ["yarn", "serve"]
