
# Google Cloud Release Notes Scraper

## What This Program Does

This is a **web scraping tool** that automatically downloads and organizes release notes from software documentation websites.
Think of it as a robot that reads Google Cloud changelog pages and creates neat summaries for you.

### The Basic Process:

1. **Visits a Google Cloud release notes webpage which you point it to**
2. **Finds all the release announcements** with dates
3. **Categorizes each update** (new features, bug fixes, breaking changes, etc.)
4. **Filters by time** (only shows updates from the last X months)
5. **Formats the output** in your preferred style (plain text, Markdown, JSON, or HTML)

### What It Looks For:

- **Dates** - When updates were released
- **Update types** - Automatically tags items as:
  - New features (GA - Generally Available)
  - Preview features (Beta/Early Access)
  - Bug fixes
  - Breaking changes
  - Security patches
  - Deprecations
  - Known issues
- **Links** - Captures related documentation URLs

## Key Benefits

### 1. **Saves Time**
- Instead of manually reading through dozens of release notes pages, you get a filtered summary in seconds
- No need to scroll through months/years of updates

### 2. **Customizable Time Range**
- Only see updates from the last 3 months, 6 months, 12 months, etc.
- Avoid information overload

### 3. **Smart Categorization**
- Automatically identifies what type of update each item is
- Makes it easy to spot critical changes (breaking changes, security fixes)
- Helps prioritize what you need to review

### 4. **Multiple Output Formats**
- **Text**: Simple, readable format for quick review
- **Markdown**: Perfect for documentation or GitHub
- **HTML**: Beautiful, styled webpage you can share with your team
- **JSON**: Machine-readable format for further processing

### 5. **Statistical Summary**
- Shows totals: how many releases, how many items
- Breaks down items by category
- Helps you understand the update velocity

### 6. **Works Across Platforms**
- Has built-in support for Google Cloud documentation
- Generic mode works with most documentation sites
- Adapts to different page structures

## Real-World Use Cases

- **DevOps Teams**: Stay current with cloud service updates without reading everything
- **Security Teams**: Quickly identify security patches across multiple services
- **Product Managers**: Track new feature releases
- **Developers**: Find breaking changes before upgrading dependencies
- **Technical Writers**: Aggregate changes for customer-facing release notes

## Example Usage

```bash
# Get last 6 months of updates as HTML
./gcpwatch.py -u https://cloud.google.com/run/docs/release-notes -m 6 -o html -f summary.html

# Get last 3 months as Markdown
./gcpwatch.py -u https://example.com/changelog -m 3 -o markdown

# Quick text summary to screen
./gcpwatch.py -u https://example.com/releases
```

## Bottom Line

This tool transforms the tedious task of monitoring software updates into an automated, organized process. It's like having an assistant who reads all the release notes for you and highlights what matters.


## Instructions

```bash
 uv venv
 source .venv/bin/activate
 uv pip install -r requirements.txt
```

### 1. **Months Parameter** (`-m` or `--months`):
```bash
# Get last 6 months of release notes
./gcpwatch.py -m 6

# Get last 12 months
./gcpwatch.py -m 12
```

### 2. **URL Option** (`-u` or `--url`):
```bash
# Scrape different Google Cloud service release notes
./gcpwatch.py -u https://cloud.google.com/storage/docs/release-notes

# Scrape Cloud Functions release notes
./gcpwatch.py -u https://cloud.google.com/functions/docs/release-notes
```

### 3. **HTML Output** (`-o html`):
```bash
# Generate HTML output with clickable links
./gcpwatch.py -o html

# Generate HTML and save to specific file
./gcpwatch.py -o html -f my_cloudrun_release_notes.html

# Combine all options
./gcpwatch.py -m 6 -u https://cloud.google.com/run/docs/release-notes -o html -f cloud_run_6months.html
```


# Google Cloud Release Notes URLs

Applications & Development
* AppHub https://cloud.google.com/app-hub/docs/release-notes
* API Gateway: https://cloud.google.com/api-gateway/docs/release-notes
* Apigee: https://cloud.google.com/apigee/docs/release-notes
* Cloud Build: https://cloud.google.com/build/docs/release-notes
* Cloud Functions: https://cloud.google.com/functions/docs/release-notes
* Cloud Run: https://cloud.google.com/run/docs/release-notes
* Cloud Tasks: https://cloud.google.com/tasks/docs/release-notes
* Cloud Trace: https://cloud.google.com/trace/docs/release-notes
* Eventarc: https://cloud.google.com/eventarc/docs/release-notes
* Workflows: https://cloud.google.com/workflows/docs/release-notes

Databases & Data Analytics
* AlloyDB for PostgreSQL: https://cloud.google.com/alloydb/docs/release-notes
* BigQuery: https://cloud.google.com/bigquery/docs/release-notes
* Cloud Data Fusion: https://cloud.google.com/data-fusion/docs/release-notes
* Cloud Firestore: https://cloud.google.com/firestore/docs/release-notes
* Cloud Spanner: https://cloud.google.com/spanner/docs/release-notes
* Cloud SQL: https://cloud.google.com/sql/docs/release-notes
* Data Catalog: https://cloud.google.com/data-catalog/docs/release-notes
* Database Migration Service: https://cloud.google.com/database-migration/docs/release-notes
* Dataflow: https://cloud.google.com/dataflow/docs/release-notes
* Dataproc: https://cloud.google.com/dataproc/docs/release-notes
* Datastore: https://cloud.google.com/datastore/docs/release-notes
* Memorystore for Memcached: https://cloud.google.com/memorystore/docs/memcached/release-notes
* Memorystore for Redis: https://cloud.google.com/memorystore/docs/redis/release-notes

Security & Identity
* Binary Authorization: https://cloud.google.com/binary-authorization/docs/release-notes
* Certificate Authority Service: https://cloud.google.com/certificate-authority-service/docs/release-notes
* Cloud Armor: https://cloud.google.com/armor/docs/release-notes
* Cloud KMS: https://cloud.google.com/kms/docs/release-notes
* IAM: https://cloud.google.com/iam/docs/release-notes
* Identity Platform: https://cloud.google.com/identity-platform/docs/release-notes
* reCAPTCHA Enterprise: https://cloud.google.com/recaptcha-enterprise/docs/release-notes
* Secret Manager: https://cloud.google.com/secret-manager/docs/release-notes
* Security Command Center: https://cloud.google.com/security-command-center/docs/release-notes
* VPC Service Controls: https://cloud.google.com/vpc-service-controls/docs/release-notes

Networking
* Cloud CDN: https://cloud.google.com/cdn/docs/release-notes
* Cloud DNS: https://cloud.google.com/dns/docs/release-notes
* Cloud Interconnect: https://cloud.google.com/network-connectivity/docs/interconnect/release-notes
* Cloud Load Balancing: https://cloud.google.com/load-balancing/docs/release-notes
* Cloud NAT: https://cloud.google.com/nat/docs/release-notes
* Cloud Router: https://cloud.google.com/router/docs/release-notes
* Cloud Service Mesh: https://cloud.google.com/service-mesh/docs/release-notes
* Cloud Virtual Private Cloud: https://cloud.google.com/vpc/docs/release-notes
* Network Intelligence Center: https://cloud.google.com/network-intelligence-center/docs/release-notes
* Network Service Tiers: https://cloud.google.com/network-tiers/docs/release-notes
* Service Directory: https://cloud.google.com/service-directory/docs/release-notes

Storage
* Artifact Registry: https://cloud.google.com/artifact-registry/docs/release-notes
* Cloud Storage: https://cloud.google.com/storage/docs/release-notes
* Container Registry: https://cloud.google.com/container-registry/docs/release-notes
* Filestore: https://cloud.google.com/filestore/docs/release-notes
* Managed Lustre: https://cloud.google.com/managed-lustre/docs/release-notes
* Transfer Appliance: https://cloud.google.com/transfer-appliance/docs/release-notes

Compute / Infrastructure
* Bare Metal Solution: https://cloud.google.com/bare-metal/docs/release-notes
* Cloud Hub: https://cloud.google.com/hub/docs/release-notes
* Cloud TPU: https://cloud.google.com/tpu/docs/release-notes
* Compute Engine: https://cloud.google.com/compute/docs/release-notes
* Confidential Space https://cloud.google.com/confidential-computing/confidential-space/docs/release-notes
* Google Distributed Cloud Connected: https://cloud.google.com/distributed-cloud/edge/latest/docs/release-notes
* Google Distributed Cloud Edge: https://cloud.google.com/distributed-cloud/edge/latest/docs/release-notes
* Google Distributed Cloud Bare: Metal https://cloud.google.com/kubernetes-engine/distributed-cloud/bare-metal/docs/release-notes
* Google Distributed Cloud VMware: https://cloud.google.com/kubernetes-engine/distributed-cloud/vmware/docs/release-notes

Google Kubernetes Engine (GKE)
* Main GKE Notes https://cloud.google.com/kubernetes-engine/docs/release-notes
* GKE Rapid https://cloud.google.com/kubernetes-engine/docs/release-notes-rapid
* GKE Regular https://cloud.google.com/kubernetes-engine/docs/release-notes-regular
* GKE Stable https://cloud.google.com/kubernetes-engine/docs/release-notes-stable
* GKE Extended https://cloud.google.com/kubernetes-engine/docs/release-notes-extended
* GKE Nochannel https://cloud.google.com/kubernetes-engine/docs/release-notes-nochannel

* VMware Engine: https://cloud.google.com/vmware-engine/docs/release-notes

Management & Operations
* Cloud Logging: https://cloud.google.com/logging/docs/release-notes
* Cloud Monitoring: https://cloud.google.com/monitoring/docs/release-notes
* Cloud Observability https://cloud.google.com/stackdriver/docs/release-notes
* Cloud Profiler: https://cloud.google.com/profiler/docs/release-notes
* Cloud Scheduler: https://cloud.google.com/scheduler/docs/release-notes
* Config Connector: https://cloud.google.com/config-connector/docs/release-notes
* Resource Manager: https://cloud.google.com/resource-manager/docs/release-notes

AI & Machine Learning
* AI Applications Builder: https://cloud.google.com/generative-ai-app-builder/docs/release-notes
* Dialogflow: https://cloud.google.com/dialogflow/docs/release-notes
* Document AI: https://cloud.google.com/document-ai/docs/release-notes
* Gemini Code Assist: https://cloud.google.com/gemini/docs/codeassist/release-notes
* Speech-to-Text: https://cloud.google.com/speech-to-text/docs/release-notes
* Talent Solution: https://cloud.google.com/talent-solution/docs/release-notes
* Text-to-Speech: https://cloud.google.com/text-to-speech/docs/release-notes
* Translation: https://cloud.google.com/translate/docs/release-notes
* Vertex AI: https://cloud.google.com/vertex-ai/docs/release-notes
* Video Intelligence API: https://cloud.google.com/video-intelligence/docs/release-notes

Specialized & Other Services
* Cloud Composer: https://cloud.google.com/composer/docs/release-notes
* Healthcare API: https://cloud.google.com/healthcare/docs/release-notes

Web3
* Blockchain Node Engine: https://cloud.google.com/blockchain-node-engine/docs/release-notes

Workspace
* Apps Script: https://developers.google.com/apps-script/release-notes
* Management: Release notes for Google Cloud Search API: https://developers.google.com/workspace/cloud-search/release-notes
* Tools: Release notes for the Google Docs API: https://developers.google.com/workspace/docs/release-notes

Unsupported
* https://cloud.google.com/sdk/docs/release-notes
* https://github.com/google-gemini/gemini-cli/releases
* https://ai.google.dev/gemini-api/docs/changelog

* https://ai.google.dev/gemini-api/docs/changelog
* https://firebase.google.com/support/releases # Won't work
* https://firebase.google.com/support/release-notes/ios # Should work
* https://firebase.google.com/support/release-notes/android # Won't work
* https://firebase.google.com/support/release-notes/js Should work
* https://firebase.google.com/support/release-notes/flutter # Should work
* https://firebase.google.com/support/release-notes/cpp-relnotes # Should work
* https://firebase.google.com/support/release-notes/unity # Should work
* https://firebase.google.com/support/release-notes/admin/node # Should work
* https://firebase.google.com/support/release-notes/admin/java # Should work
* https://firebase.google.com/support/release-notes/admin/python # Should work
* https://firebase.google.com/support/release-notes/admin/go # Should work
* https://firebase.google.com/support/release-notes/admin/dotnet # Should work
* https://firebase.google.com/support/release-notes/security-rules # Won't work
* https://firebase.google.com/support/release-notes/cli # Should work
* https://firebase.google.com/support/release-notes/firebase-studio # Should work

## Screengrabs
<img width="1262" height="713" alt="Screenshot 2025-10-04 at 11 20 04" src="https://github.com/user-attachments/assets/0c8dc809-8d97-4005-aa22-5c08682282b6" />


