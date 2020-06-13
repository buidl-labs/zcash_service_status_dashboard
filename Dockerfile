FROM ubuntu:latest

RUN apt-get update 

# RUN apt-get install -y curl

# RUN apt-get -y install systemd

RUN apt-get install -y locales && \
    localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8

ENV LANG en_US.utf8

# Setup `zcash_service_status_dashboard` source code
RUN apt-get install -y python3-pip

# Update the system after all packages were installed
RUN apt-get update

# Remove extra repositories from apt and apt-get for space
RUN rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/ubuntu/production/zcash_service_status_dashboard

COPY ./* /home/ubuntu/production/zcash_service_status_dashboard/

WORKDIR /home/ubuntu/production/zcash_service_status_dashboard

RUN pwd

RUN pip3 install -r requirements.txt

# Install Prometheus
# RUN mkdir /etc/prometheus
# RUN mkdir /var/lib/prometheus
# WORKDIR /home/ubuntu
# RUN curl -LO https://github.com/prometheus/prometheus/releases/download/v2.0.0/prometheus-2.0.0.linux-amd64.tar.gz
# RUN tar xvf prometheus-2.0.0.linux-amd64.tar.gz
# RUN cp prometheus-2.0.0.linux-amd64/prometheus /usr/local/bin/
# RUN cp prometheus-2.0.0.linux-amd64/promtool /usr/local/bin/
# RUN cp -r prometheus-2.0.0.linux-amd64/consoles /etc/prometheus
# RUN cp -r prometheus-2.0.0.linux-amd64/console_libraries /etc/prometheus
# RUN rm -rf prometheus-2.0.0.linux-amd64.tar.gz prometheus-2.0.0.linux-amd64

# Configure Prometheus
# RUN rm -rf /etc/systemd/system/prometheus.service
# RUN cp /home/ubuntu/production/zcash_service_status_dashboard/prometheus.service /etc/systemd/system/

# Run Prometheus
# RUN systemctl daemon-reload
# RUN service prometheus start

# Keep the container running
CMD tail -f /dev/null