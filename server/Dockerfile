FROM node:22-alpine

WORKDIR /app

COPY . .

RUN npm install 

EXPOSE 8001

RUN npm run eslint

CMD ["npm", "start"]
