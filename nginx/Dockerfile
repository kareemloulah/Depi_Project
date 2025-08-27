FROM nginx:stable-alpine-perl

COPY ./default.conf /etc/nginx/conf.d/default.conf
COPY ./nginx.conf /etc/nginx/nginx.conf
COPY ./certs/* /etc/nginx/certs/
EXPOSE 80
EXPOSE 443

CMD ["nginx", "-g", "daemon off;"]