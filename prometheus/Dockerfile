FROM prom/prometheus:v2.53.4

COPY ./prometheus.yml /etc/prometheus/prometheus.yml

EXPOSE 9090

CMD ["--config.file=/etc/prometheus/prometheus.yml", "--storage.tsdb.path=/prometheus", "--web.console.libraries=/etc/prometheus/console_libraries", "--web.console.templates=/etc/prometheus/consoles" , "--web.external-url=https://ec2-18-169-104-105.eu-west-2.compute.amazonaws.com/prometheus/"]

