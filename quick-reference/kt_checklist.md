[🏠 Home](../README.md) · [Quick Reference](batch_state.md)

# 📋 Knowledge Transfer (KT) Completion Checklist

> **Purpose:** Everything to collect/verify BEFORE the KT is marked done.
> Don't let the person leaving walk out the door until every item is checked.

---

## How to Use This Checklist

Copy this into a working doc. Tick items as you get them. Share the incomplete list with the outgoing person — it makes the conversation easier.

```
  Rule: If it's not documented, it doesn't exist.
  Rule: If only one person knows it, it's a risk.
  Rule: Test every access before the KT ends.
```

---

## 1. ☁️ Cloud & Infrastructure Access

- [ ] **Cloud portal access** — Azure subscription / AWS account / GCP project (confirm which subscriptions you need)
- [ ] **Cloud role confirmed** — verify you have at minimum Contributor on the relevant resource groups
- [ ] **Resource group inventory** — get a list of all resource groups and what lives in each
- [ ] **Terraform/IaC state** — know where the Terraform state file is (Azure Blob, Terraform Cloud, S3)
- [ ] **Infra architecture diagram** — up-to-date diagram of all resources and how they connect

---

## 2. 🔑 VM & Server Access

- [ ] **All VM SSH PEM files** — for every environment (dev, staging, prod, DR)
  - Production VMs: `/path/to/pem/vm-prod.pem`
  - Staging VMs: `/path/to/pem/vm-staging.pem`
- [ ] **VM IP addresses / hostnames** — list of all servers with their function
- [ ] **Default SSH username** — `azureuser`, `ubuntu`, `ec2-user` — confirm per VM
- [ ] **Sudo/root access** — confirm if you need it and have it
- [ ] **Bastion / Jump server access** — credentials + connection method (browser or SSH tunnel)
- [ ] **VPN config + certificates** — VPN client config + any required certs for on-prem or private network access
- [ ] **Windows RDP credentials** — username + password for any Windows servers
- [ ] **Windows Server license keys** — if self-managed

---

## 3. 🗄️ Database Access

- [ ] **Database host/endpoint** — hostname or private IP for each DB
- [ ] **Database port** — standard (5432 PG, 3306 MySQL, 1433 MSSQL) or non-standard?
- [ ] **Database name** — list of all databases and their purpose
- [ ] **Admin credentials** — username + password for each DB (store in Key Vault, not email)
- [ ] **DB PEM/SSL certificate** — if DB requires SSL client auth (PostgreSQL ssl-mode=require, RDS)
- [ ] **Connection string** — full connection string per environment (app config format)
- [ ] **Managed DB access** — if Azure SQL / RDS — confirm portal/CLI access to the DB service itself
- [ ] **pgAdmin / MySQL Workbench access** — ensure GUI tool is configured and connecting
- [ ] **Read replica endpoints** — if any (separate from write endpoint)
- [ ] **Backup schedule** — how often, where stored, how to restore

---

## 4. 🔐 Secrets, Credentials & Keys

- [ ] **Key Vault name and resource group** — which vault holds what
- [ ] **Key Vault access** — confirm you can read secrets (`Key Vault Secrets User` role)
- [ ] **All secret names** — get a documented list of every secret stored in the vault
- [ ] **API keys (third-party)** — Datadog, PagerDuty, Twilio, SendGrid, payment gateways, etc.
- [ ] **Service Principal client IDs + expiry dates** — document them in a spreadsheet
  - Name, Client ID, Scope, Expiry Date, Where it's used
- [ ] **SSL/TLS certificates** — domain name, expiry date, renewal process, who is the CA
- [ ] **Container registry credentials** — ACR/ECR/GHCR login details
- [ ] **CI/CD service connection secrets** — GitHub secrets, Azure DevOps variable groups
- [ ] **Signing keys** — JWT signing secrets, code signing certificates, SSH deploy keys

---

## 5. 🌐 DNS & Networking

- [ ] **Domain registrar login** — GoDaddy, Namecheap, Google Domains — URL + credentials
- [ ] **DNS zone access** — confirm access to the DNS provider (Azure DNS, Route 53, Cloudflare)
- [ ] **DNS records documented** — export all DNS records (`az network dns record-set list`) or screenshot
- [ ] **Nameserver delegation** — confirm which NS serves the domain (check at registrar)
- [ ] **SSL cert issuer** — Let's Encrypt (auto-renew?), DigiCert, Azure-managed?
- [ ] **All subdomains** — list of every subdomain and what it points to
- [ ] **Private DNS zones** — list of internal zones and VNet links
- [ ] **Firewall rules** — NSG rules, Azure Firewall policies, on-prem firewall rules
- [ ] **VNet topology** — peering layout, VPN gateways, private endpoints
- [ ] **Load balancer rules** — backend pools, health probe endpoints, listener rules

---

## 6. ⚙️ CI/CD & Azure DevOps / GitHub

- [ ] **Azure DevOps organization access** — URL + your role (Project Admin minimum)
- [ ] **GitHub organization access** — org member + appropriate repo permissions
- [ ] **Service connections** — list all, confirm they work (run a test pipeline)
- [ ] **Variable groups** — list + contents documented (non-secret values at minimum)
- [ ] **Secure files** — any certs or configs stored in Library → Secure Files
- [ ] **Pipeline walkthrough** — outgoing person walks you through the full CI/CD flow
- [ ] **Self-hosted agent pools** — where are agents running? How to restart them?
- [ ] **Environment approvers** — who is set as approver for UAT, Prod, DR environments?
- [ ] **Artifact feeds** — npm/NuGet/pip feeds in Azure Artifacts or Artifactory
- [ ] **Container registry push/pull access** — confirm pipeline can push and VMs/AKS can pull

---

## 7. ☸️ Kubernetes / AKS

- [ ] **kubeconfig file** — `~/.kube/config` or `az aks get-credentials` command
- [ ] **Cluster name + resource group** — for each cluster (dev, staging, prod)
- [ ] **Namespaces** — list of all namespaces and their purpose
- [ ] **Helm releases** — list of all deployed Helm charts (`helm list -A`)
- [ ] **Secrets in K8s** — any secrets not in Key Vault (check for `kubectl get secret -A`)
- [ ] **Ingress config** — ingress controller, domains, TLS certs
- [ ] **Node pools** — system + app node pools, spot pools, autoscaler settings
- [ ] **KEDA / HPA settings** — autoscaling configuration

---

## 8. 📊 Monitoring & Alerting

- [ ] **Monitoring platform access** — Azure Monitor, Grafana, Datadog, Prometheus
- [ ] **Dashboards** — URLs or exports of key dashboards
- [ ] **Alert rules** — what triggers what, who gets notified
- [ ] **PagerDuty / OpsGenie** — on-call schedule + escalation policies
- [ ] **Log Analytics workspace** — workspace ID + access confirmed
- [ ] **Application Insights** — instrumentation keys per environment
- [ ] **Cost budget alerts** — who gets alerted when budget exceeds thresholds

---

## 9. 📚 Documentation & Runbooks

- [ ] **Architecture diagram** — up-to-date system design doc
- [ ] **Deployment runbook** — step-by-step how to deploy manually if pipeline fails
- [ ] **Incident response playbook** — what to do when prod is down
- [ ] **Rollback procedure** — how to revert a bad deployment
- [ ] **On-call contacts** — names, phone numbers, escalation path
- [ ] **Vendor contacts** — support contacts for cloud provider, registrar, SaaS tools
- [ ] **Post-mortem / known issues doc** — ongoing or past incidents that left a residue
- [ ] **Cron job inventory** — list of ALL cron jobs (Linux crontab, Azure Functions, Logic Apps)
- [ ] **DR plan** — RTO/RPO targets, DR runbook, last DR drill date

---

## 10. 🔒 Compliance & Governance

- [ ] **Azure Policy assignments** — what policies are enforced and on which scope
- [ ] **Resource locks** — list resources with Delete or Read-Only locks
- [ ] **Tag conventions** — what tags are mandatory and what values they take
- [ ] **Cost budgets** — budget name, amount, alert thresholds
- [ ] **Data classification** — which data is PII/PCI/HIPAA and where it lives
- [ ] **Compliance reports** — any active certifications (ISO 27001, SOC 2) or audit schedule

---

## 11. ✅ Final Verification Before Closing KT

Do these as the LAST step — before saying "KT is done":

- [ ] SSH into at least one production VM with the provided PEM
- [ ] Connect to the database with provided credentials from your machine
- [ ] Run a test pipeline end-to-end (even a no-op pipeline)
- [ ] Read a secret from Key Vault using your identity
- [ ] Confirm DNS records by running `dig yourapp.com`
- [ ] Browse the monitoring dashboard and confirm data is flowing
- [ ] Trigger a test alert and confirm you receive the notification
- [ ] Verify you can list AKS nodes: `kubectl get nodes`
- [ ] Confirm you received access to the document store (Confluence, Notion, SharePoint)

---

## Gotchas ⚠️

### Don't trust "you have access" — test it
People often say "I'll give you access" and forget. Verify every access item yourself before the KT call ends. A `.pem` file sent via email might be for the wrong key. Test the SSH connection.

### SSL cert expiry dates are land mines
Get all SSL cert expiry dates in a spreadsheet with calendar reminders set 30 days before. An expired cert means your site shows a security warning — and it will expire at the worst possible time.

### Service principal secrets will expire and break pipelines
Get every SP name + expiry date. Set reminders. Better yet, migrate to OIDC during the handoff.

### Undocumented cron jobs are the #1 hidden surprise
Ask explicitly: "Are there any cron jobs, scheduled tasks, Logic Apps, or Azure Functions running on a schedule?" These are almost never documented and often break after handoff because no one knew they existed.

### DNS changes need advance notice
If you need to change any DNS records, remember the TTL effect. If the current TTL is 86400, a DNS change takes up to 24 hours to propagate. Lower TTL well in advance.

### Test database restore — don't just assume backups work
Get the backup schedule, location, and restoration procedure. Then actually test restoring a non-prod database from backup. "We have backups" and "we can restore from backups" are two very different statements.

### Get PEM files before the person's last day
Once their access is revoked, you may not be able to regenerate the key pair for existing VMs.

---

*Source: Synthesised from all trainee-docs handbooks + DevOps domain knowledge*
