# ZCash Service Status Dashboard
This readme deals with installation and setup instructions for building a health-check system for ZCash communities and exchanges. For a detailed look, visit [here](https://zcashservicestatus.info).

The health check system involves three tools: Prometheus, Blackbox Exporter and Grafana. There is one Python script which iterates over twelve exchanges to extract and load the data in the dashboard. 

## Installing Prometheus:
```
wget https://s3-eu-west-1.amazonaws.com/deb.robustperception.io/41EFC99D.gpg | sudo apt-key add -
sudo apt-get update -y
sudo apt-get install prometheus prometheus-node-exporter prometheus-pushgateway prometheus-alertmanager -y
```
Once the installation is completed, start Prometheus service and enable it to start on boot time with the following command:
```
sudo systemctl start prometheus
sudo systemctl enable prometheus
```
You can also check the status of Prometheus service with the following command:
`sudo systemctl status prometheus`

Now, configure the prometheus' config file with the following content:
```
# Sample config for Prometheus.

global:
  scrape_interval:     15s # By default, scrape targets every 15 seconds.
  evaluation_interval: 15s # By default, scrape targets every 15 seconds.
  # scrape_timeout is set to the global default (10s).

  # Attach these labels to any time series or alerts when communicating with
  # external systems (federation, remote storage, Alertmanager).
  external_labels:
      monitor: 'example'

# Load and evaluate rules in this file every 'evaluation_interval' seconds.
rule_files:
  # - "first.rules"
  # - "second.rules"

# A scrape configuration containing exactly one endpoint to scrape:
# Here it's Prometheus itself.
scrape_configs:
  # The job name is added as a label `job=<job_name>` to any timeseries scraped from this config.
  - job_name: 'prometheus'

    # Override the global default and scrape targets from this job every 5 seconds.
    scrape_interval: 5s
    scrape_timeout: 5s

    # metrics_path defaults to '/metrics'
    # scheme defaults to 'http'.

    static_configs:
      - targets: ['localhost:9090']
  
  - job_name: 'exchanges'

    # Override the global default and scrape targets from this job every 5 seconds.
    scrape_interval: 5s
    scrape_timeout: 5s

    # metrics_path defaults to '/metrics'
    # scheme defaults to 'http'.

    static_configs:
      - targets: ['localhost:8093']

  - job_name: node
    # If prometheus-node-exporter is installed, grab stats about the local
    # machine by default.
    static_configs:
      - targets: ['localhost:9100']

  - job_name: blackbox
    metrics_path: /probe
    params:
      module: [http_2xx]
    static_configs:
      - targets:
        - https://chat.zcashcommunity.com/home
        - https://forum.zcashcommunity.com/
        - https://www.zcashcommunity.com/
        - https://z.cash/
        - https://www.zfnd.org/
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: 127.0.0.1:9115 # The blackbox exporter.
```
Restart the prometheus server so as to make the changes reflected:
```
sudo service prometheus restart
sudo service prometheus status
```

## Installing Grafana
```
sudo apt-get install -y software-properties-common
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
sudo apt-get update
sudo apt-get install grafana
sudo apt-get install -y apt-transport-https
sudo service grafana-server start
sudo service grafana-server status
```

## Installing Blackbox Exporter
```
wget https://github.com/prometheus/blackbox_exporter/releases/download/v0.14.0/blackbox_exporter-0.14.0.linux-amd64.tar.gz .
tar -vxzf blackbox_exporter-0.14.0.linux-amd64.tar.gz
cd blackbox_exporter-0.14.0.linux-amd64/
```
Now, replace the content of `blackbox.yml` with the following:
```
modules:
  http_2xx:
    http:
      preferred_ip_protocol: "ip4"
      ip_protocol_fallback: false
    prober: http
  http_post_2xx:
    prober: http
    http:
      method: POST
  tcp_connect:
    prober: tcp
  pop3s_banner:
    prober: tcp
    tcp:
      query_response:
      - expect: "^+OK"
      tls: true
      tls_config:
        insecure_skip_verify: false
  ssh_banner:
    prober: tcp
    tcp:
      query_response:
      - expect: "^SSH-2.0-"
  irc_banner:
    prober: tcp
    tcp:
      query_response:
      - send: "NICK prober"
      - send: "USER prober prober prober :prober"
      - expect: "PING :([^ ]+)"
        send: "PONG ${1}"
      - expect: "^:[^ ]+ 001"
  icmp:
    prober: icmp

```
./blackbox_exporter --config.file="blackbox.yml"

# Install Dependencies
```
sudo apt-get install python3-pip
pip3 install prometheus-client==0.7.1
```

Now, run the command `python3 driver_exchanges_health_check.py` in order to run the script for all the health checks on exchanges.


Install NGINX and apply SSL using Let'sEncrypt.

Note: This readme will be further updated with 'why' section and some FAQs. Please feel free to open any issue and provide us your valuable feedback.
