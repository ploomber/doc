FROM node

RUN npm install -g serve
WORKDIR /app

COPY package.json /app/package.json
RUN npm install

COPY . /app
RUN npm run build

ENTRYPOINT ["serve", "-s", "build", "-p", "80"]