# New Relic Alert Intelligence — Correlation Details

> **When to load:** Phase 2 (Configure) — setting up custom correlation decisions, topology, Smart Alerts, and understanding the Correlation Platform roadmap.

## Custom Decision Builders

### Basic Builder
- Correlate by attributes (up to 8 filters)
- Filter by specific values
- Filter by related entities (topology)
- Set correlation time range (1-120 min, default 20)
- Test with simulation (7 days historical)

### Advanced Builder
- Different filters per alert event segment
- Attribute similarity with configurable algorithms
- Regex matching (Java pattern standard)
- Priority override, minimum event count settings

## 9 Similarity Algorithms

| Algorithm | Best For |
|-----------|---------|
| Levenshtein Distance | Short strings, typos, minor variations |
| Fuzzy Score | Same-length strings with matching prefixes |
| Fuzzy Wuzzy Ratio | Very short or very long strings of similar length |
| Fuzzy Wuzzy Partial Ratio | 3-10 word strings with overlapping substrings |
| Fuzzy Wuzzy Token Set Ratio | Different word order (messages, descriptions) |
| Jaro-Winkler | Short strings with identical prefixes (0.9 threshold recommended) |
| Cosine Distance | Large text blocks, descriptions |
| Hamming Distance | Same-length strings with positional differences |
| Jaccard Distance | Large data sets, entire alert events |

## Topology Correlation

Uses entity relationship graph (service map). Checks if entities are connected within **5 hops**.

Auto-discovered from NR agents (distributed tracing, infra agent, K8s integration). Custom topology via NerdGraph API:

```graphql
# Create vertices
mutation {
  aiTopologyCollectorCreateVertices(
    accountId: ACCOUNT_ID
    vertices: [{
      name: "ServiceA"
      vertexClass: APPLICATION
      definingAttributes: [{ key: "entity.guid", value: "GUID" }]
    }]
  ) { result }
}

# Create edges
mutation {
  aiTopologyCollectorCreateEdges(
    accountId: ACCOUNT_ID
    edges: [{
      directed: true
      fromVertexName: "ServiceA"
      toVertexName: "Host1"
    }]
  ) { result }
}
```

## Correlation Assistant
- Navigate: `Alerts > Issues & activity > Alert events`
- Select events, click **Correlate alert events**
- Choose low-frequency attributes for best results
- Exact match + Levenshtein similarity analysis
- Simulate against 7 days of data before saving

---

## Smart Alerts (Preview)

UI-driven framework that automates alert coverage using pre-packaged **Condition Standards**. Reduces setup from 20-40 clicks per entity to 5-6 clicks at scale.

### Condition Standards by Entity Type

| Entity Type | Standards |
|-------------|----------|
| APM Services | Response time, Throughput (high/low), Error rate |
| Browser Apps | INP, LCP, Page load time, JS error rate |
| Synthetic Monitors | Duration, Failures |

### Coverage Categories
- **Fully covered** — All relevant standards applied
- **Partial** — Some standards missing
- **Uncovered** — No alerting

### Setup Flow
1. Review coverage at `Alerts > Alerts Overview`
2. Click **Manage coverage**
3. Apply standards: **Cover all gaps** (bulk) / **Cover (N)** (by type) / **Configure** (custom)
4. Optional: adjust thresholds (histogram view), add tag filters, set issue preference
5. Creates conditions that **auto-apply to new matching entities**

### Alert Quality Management
- **Noise overview** — Identifies high-volume noisy conditions
- **Conditions without signals** — Stale alerts (no data for 30 days)
- **Notification failures** — Delivery issues in last 24 hours

### Limitations
- **No Terraform/NerdGraph support** — UI only
- Creates conditions for ALL matching entities (risk of duplicates)
- Must use filters to exclude entities (tags: environment, team, etc.)

---

## NR Correlation Platform (Future — Internal PRD)

### Philosophy: "Insight-First, Configuration-Optional"
- Pre-correlated insights shown immediately, no setup required
- Suppression NEVER default — gated behind: Correlation + IRCA causality + High confidence + Good data quality

### 4-Zone Landing Page
1. **Patterns That Matter** — Dominant explanatory dimensions
2. **What's New/Changing** — Pattern evolution vs 7-day baseline
3. **Where to Act** — Prioritized clusters ranked by operational relevance
4. **Health & Trust** — Noise reduction metrics, accuracy signals

### 3-Phase Rollout
- **Phase 1 (MVP)**: NR/AWS/Azure/ServiceNow ingestion, attribute+temporal correlation, landing page, simulation
- **Phase 2**: IRCA integration, closing-the-loop metrics, confidence indicators
- **Phase 3**: Child alert suppression, confidence-gated policies, auto-remediation

### 5 Rule Creation Paths
Templates, Template editing, Wizard, Natural language, Query-based
