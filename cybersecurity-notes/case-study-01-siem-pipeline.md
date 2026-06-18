# Case Study 1 — LogStream: Minimalist SIEM Pipeline
> Building a centralized logging and alerting system from scratch.

## 1. Project Overview
**LogStream** is a lightweight, scalable Security Information and Event Management (SIEM) pipeline designed to aggregate, parse, and analyze infrastructure logs in real-time. It targets small-to-medium security teams (SOC analysts and sysadmins) who need deep visibility into their networks without the overhead of heavy commercial SIEM solutions.

**Core Capabilities:**
- Collects system (`auth.log`, `syslog`) and network logs across multiple Linux/Windows endpoints.
- Normalizes disparate log formats into a structured JSON schema using Logstash.
- Stores logs securely in an Elasticsearch datastore for rapid querying.
- Triggers real-time alerts on Indicators of Compromise (IoCs) like SSH brute-force attacks and abnormal port scans.
- Provides SOC analysts with centralized Kibana dashboards for threat hunting and incident response.

## 2. Architecture Diagram (ASCII)

```text
       +-------------------+       
       |   Endpoints       |       
       | (Web, DB, App)    |       
       | [Filebeat/Auditd] |       
       +--------+----------+       
                | (JSON / Raw Logs over TCP/TLS)
                v
       +-------------------+       
       |   Forwarders /    |       
       |   Parser          |       
       |   [Logstash]      |       
       +--------+----------+       
                | (Structured JSON)
                v
       +-------------------+       
       |   Datastore       | <---------------+
       | [Elasticsearch]   |                 |
       +--------+----------+                 |
                |                            | (Queries)
      +---------+---------+                  |
      |                   |                  |
      v                   v                  |
+-------------+     +-------------+          |
|  Alerting   |     |  Dashboard  |----------+
| [ElastAlert]|     |  [Kibana]   |
+-------------+     +-------------+
      |                   
      v                   
[Slack/Email]             
```

## 3. Tech Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Log Shippers** | Filebeat, Auditbeat | Lightweight agents deployed on edge nodes to read log files and forward them. |
| **Parser / Aggregator** | Logstash | Ingests raw data, groks (parses) text into structured fields, adds geo-IP data, and sends to the database. |
| **Datastore** | Elasticsearch | Distributed, RESTful search and analytics engine for high-performance log storage. |
| **Visualization** | Kibana | Web interface for data exploration, dashboarding, and visual threat hunting. |
| **Alerting** | ElastAlert 2 | Python-based framework that polls Elasticsearch for anomalies and triggers webhooks/emails. |

## 4. Step-by-Step Build (Phases)

**Phase 1: Endpoint Instrumentation (Collection)**
We deploy Filebeat to all target servers. We configure `filebeat.yml` to monitor `/var/log/auth.log` and `/var/log/syslog` and point the output to our centralized Logstash instance rather than directly to Elasticsearch. This ensures we can buffer and parse heavily before indexing.

**Phase 2: Log Normalization (Parsing)**
We configure Logstash with input pipelines on port 5044. We write `grok` patterns to extract timestamp, IP addresses, usernames, and action types (e.g., `Failed password` or `Accepted publickey`). We map these to the Elastic Common Schema (ECS) to ensure consistent querying.

**Phase 3: Hot/Warm Storage (Indexing)**
Logs are pushed into Elasticsearch. We implement an Index Lifecycle Management (ILM) policy: logs stay in the "Hot" tier (fast SSDs) for 7 days, move to "Warm" storage for 30 days, and are deleted (or archived to S3) after 90 days to control costs.

**Phase 4: Alerting & Visualization (Action)**
Kibana dashboards are built to show failed login maps (via GeoIP) and traffic spikes. ElastAlert 2 is configured with YAML rules to continuously query the index. If >5 failed SSH attempts occur from the same IP within 10 minutes, an alert is fired to the `#soc-alerts` Slack channel.

## 5. Config Snippets

### Logstash Pipeline (`logstash.conf`)
*Normalizing SSH authentication logs using Grok filters.*

```text
input {
  beats {
    port => 5044
  }
}

filter {
  if [fileset][name] == "auth" {
    grok {
      match => { 
        "message" => "%{SYSLOGTIMESTAMP:system.auth.timestamp} %{SYSLOGHOST:system.auth.hostname} sshd(?:\[%{POSINT:system.auth.pid}\])?: %{DATA:system.auth.ssh.event} %{DATA:system.auth.ssh.method} for (invalid user )?%{DATA:system.auth.user} from %{IPORHOST:system.auth.ip} port %{NUMBER:system.auth.port} ssh2(: %{GREEDYDATA:system.auth.ssh.signature})?" 
      }
    }
    date {
      match => [ "system.auth.timestamp", "MMM  d HH:mm:ss", "MMM dd HH:mm:ss" ]
      target => "@timestamp"
    }
    geoip {
      source => "system.auth.ip"
      target => "geo"
    }
  }
}

output {
  elasticsearch {
    hosts => ["http://elasticsearch:9200"]
    index => "logstream-auth-%{+YYYY.MM.dd}"
  }
}
```

### ElastAlert 2 Rule (`ssh-brute-force.yaml`)
*Detecting SSH brute-force attempts.*

```yaml
name: SSH Brute Force Detection
type: frequency
index: logstream-auth-*
num_events: 5
timeframe:
  minutes: 10

filter:
- query_string:
    query: "system.auth.ssh.event: \"Failed password\""

query_key: "system.auth.ip"

alert:
- "slack"
slack:
slack_webhook_url: "https://hooks.slack.com/services/T0000/B0000/XXXX"
slack_username_override: "SOC Bot"
slack_title: "🚨 Possible SSH Brute Force Detected"
slack_text_string: "Detected {0} failed login attempts from IP {1} targeting user {2}."
slack_text_args:
- num_hits
- system.auth.ip
- system.auth.user
```

## 6. Deployment Steps

We use Docker Compose to stand up the pipeline locally for development and testing.

**`docker-compose.yml` for the ELK Stack:**
```yaml
version: '3.8'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.10.2
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false # Set true for prod!
      - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
    ports:
      - "9200:9200"
    volumes:
      - es_data:/usr/share/elasticsearch/data

  logstash:
    image: docker.elastic.co/logstash/logstash:8.10.2
    volumes:
      - ./pipeline:/usr/share/logstash/pipeline
    ports:
      - "5044:5044"
    depends_on:
      - elasticsearch

  kibana:
    image: docker.elastic.co/kibana/kibana:8.10.2
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch

  elastalert:
    image: jertel/elastalert2:latest
    volumes:
      - ./elastalert-rules:/opt/elastalert/rules
    depends_on:
      - elasticsearch

volumes:
  es_data:
```
**Execution:**
1. Place `logstash.conf` in `./pipeline/` and `ssh-brute-force.yaml` in `./elastalert-rules/`.
2. Run `docker-compose up -d`.
3. Access Kibana at `http://localhost:5601`.
4. Install Filebeat on a target machine, point it to `http://<logstash-ip>:5044`, and start the Filebeat service.

## 7. Evaluation & Monitoring
To ensure the pipeline handles log volume efficiently, we monitor the following metrics using Kibana Stack Monitoring:
- **Indexing Rate:** Tracked to ensure Elasticsearch keeps up with incoming EPS (Events Per Second).
- **JVM Heap Usage:** For both ES and Logstash, maintaining heap below 75% is critical to prevent OutOfMemory errors and garbage collection pauses.
- **Search Latency:** Measured to ensure dashboards load quickly and ElastAlert rules do not time out.

## 8. Cost Analysis
For a mid-sized deployment processing 50 GB/day:
- **Compute (AWS EC2):** 3x `m5.xlarge` instances for Elasticsearch cluster, 1x `c5.large` for Logstash/Kibana (~$500/month).
- **Storage (EBS):** 1.5 TB gp3 storage for 30-day retention (~$120/month).
- **Bandwidth/Transfer:** Minimal if resources are in the same VPC.
- **Total:** ~$620/month. Significantly cheaper than per-GB ingestion pricing models of commercial SaaS SIEMs.

## 9. Production Gotchas

- **Indexing Bottlenecks:** A poorly written `grok` pattern (especially those heavily relying on `GREEDYDATA` combined with failing regex matches) can spike Logstash CPU and bottleneck the entire ingestion pipeline. Always test Grok patterns extensively.
- **Alert Fatigue:** Initially, SOC analysts received alerts for every failed root login attempt. Given the background noise of the internet, this resulted in thousands of alerts. We resolved this by tuning threshold windows and ignoring known scanner IPs.
- **Log Retention Costs:** Storing massive volumes of verbose logs (`DEBUG` level) quickly exhausts disk space. Strict Index Lifecycle Management (ILM) must be enforced to drop low-value data.
- **Security in Transit:** The `docker-compose` above sets `xpack.security.enabled=false`. In production, TLS must be enabled for Beat-to-Logstash and Logstash-to-Elasticsearch communication to prevent eavesdropping.

## 10. Lessons Learned

1. **Schema Consistency is King:** Adopting the Elastic Common Schema (ECS) early saved countless hours. Normalizing fields like `source.ip` and `user.name` across different log sources meant we only needed one set of dashboards and alerting rules.
2. **Decouple Ingestion from Storage:** Using Logstash (or a Kafka queue for larger setups) as a buffer prevents Elasticsearch from being overwhelmed during log spikes (e.g., during an active DDoS attack).
3. **Start Small with Alerts:** It is far better to have 3 highly actionable alerts than 100 noisy ones. Alerts should require action; if they don't, they belong in a dashboard, not a Slack channel.
