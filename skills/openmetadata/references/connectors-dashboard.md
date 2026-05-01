# OpenMetadata Dashboard / BI Connectors

Dashboard connectors publish chart, dashboard, and (sometimes) upstream-query lineage. All use `sink: metadata-rest` and the `DashboardMetadata` source config type.

## Enterprise BI

| Connector | `type` | Auth | Common gotcha |
|---|---|---|---|
| Tableau | `Tableau` | PAT (preferred) or username/password | `siteName` required for Tableau Online; lineage needs `includeDataSources: true` |
| Looker | `Looker` | API3 client ID + secret | LookML git repo optional but unlocks column-level lineage |
| PowerBI | `PowerBI` | service-principal (Azure AD) | `tenantId` + workspace scope; import mode vs DirectQuery affects lineage |
| MicroStrategy | `MicroStrategy` | username/password + project | Uses report-level granularity — dossiers only |
| Qlik Sense | `QlikSense` | certificates | On-prem uses cert-based auth; cloud uses API key |
| Qlik Cloud | `QlikCloud` | API key | Different connector from on-prem Qlik Sense |
| Sigma | `Sigma` | API client credentials | Workbook as dashboard; pages as charts |

## Self-service / modern BI

| Connector | `type` | Auth | Common gotcha |
|---|---|---|---|
| Apache Superset | `Superset` | username/password | Lineage only when datasets reference catalogued tables |
| Metabase | `Metabase` | username/password or API key | Dashboard questions are queries — enable `includeDashboards: true` |
| Mode | `Mode` | API token | Reports map to dashboards; collections not modeled |
| Redash | `Redash` | API key | No lineage; metadata only |
| Lightdash | `Lightdash` | API key | dbt-backed; requires dbt ingestion for full lineage |
| Domo | `DomoDashboard` | client ID + secret | Card-level metadata only |

## Cloud-native / embedded

| Connector | `type` | Auth | Common gotcha |
|---|---|---|---|
| AWS QuickSight | `QuickSight` | IAM role | `awsAccountId` required; SPICE-backed datasets list as separate tables |
| Google Data Studio / Looker Studio | `LookerStudio` | OAuth | Limited to datasources — report charts partial |
| Grafana | `Grafana` | API token | Panels map to charts; datasource JSON needed for lineage |

## Configuration tips common to dashboard connectors

- Use `dashboardFilterPattern` / `chartFilterPattern` rather than ingesting everything — BI tools have many draft dashboards.
- Lineage requires the upstream **database service** to already be ingested (by serviceName). If Snowflake is `snowflake` in the catalog but the BI tool references it as `snowflake_prod`, lineage misses.
- Set `markDeletedDashboards: true` to reflect retirement.
