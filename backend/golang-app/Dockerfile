FROM golang:1.23-alpine

WORKDIR /golang-app

COPY . .

RUN go mod tidy

CMD ["go", "run", "main.go"]
