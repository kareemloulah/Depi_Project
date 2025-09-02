FROM node:22-alpine

WORKDIR /app

COPY ./*.json  .

RUN npm install 

COPY . .

EXPOSE 8001


CMD ["npm", "start"]
