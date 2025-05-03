# 使用 Node.js 的官方映像作為基礎
FROM node:16

# 設置容器內的工作目錄
WORKDIR /app

# 複製 package.json 和 package-lock.json 以便安裝依賴
COPY package*.json ./

# 安裝所有依賴
RUN npm install

# 複製所有檔案到容器內
COPY . .

# 編譯應用（假設你的 NestJS 應用是用 TypeScript）
RUN npm run build

# 啟動 NestJS 應用
CMD ["npm", "run", "start:prod"]
