# 使用 Node.js 14 作為基底
FROM node:14.18.2-buster

# 設定工作目錄
WORKDIR /app

# 安裝必要的工具與 Vue CLI
RUN apt-get update -y && \
  apt-get upgrade -y && \
  apt-get install -y \
  build-essential \
  curl \
  nmap \
  git \
  nano \
  && rm -rf /var/lib/apt/lists/*

RUN npm install -g @vue/cli@4.5.15


# 啟動開發伺服器
CMD ["yarn", "serve"]

