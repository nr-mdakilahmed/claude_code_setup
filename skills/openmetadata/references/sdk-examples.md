# OpenMetadata — Python SDK Examples

> **When to load:** Phase 3 (Advanced) — programmatic CRUD, search, lineage, and test suite management via the Python SDK.

## Initialize Connection

```python
from metadata.ingestion.ometa.ometa_api import OpenMetadata
from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import (
    OpenMetadataConnection,
)

server_config = OpenMetadataConnection(
    hostPort="http://localhost:8585/api",
    authProvider="openmetadata",
    securityConfig={"jwtToken": "your-jwt-token"},
)

metadata = OpenMetadata(server_config)
```

## Get Entity by FQN

```python
from metadata.generated.schema.entity.data.table import Table

table = metadata.get_by_name(
    entity=Table,
    fqn="snowflake.database.schema.table_name",
    fields=["columns", "owner", "tags"]
)
```

## Create Test Suite and Test Case

```python
from metadata.generated.schema.api.tests.createTestSuite import CreateTestSuiteRequest
from metadata.generated.schema.api.tests.createTestCase import CreateTestCaseRequest

# Create Test Suite
test_suite = metadata.create_or_update(CreateTestSuiteRequest(
    name="my_test_suite",
    description="Data quality tests",
    executableEntityReference="service.database.schema.table"
))

# Create Test Case
test_case = metadata.create_or_update(CreateTestCaseRequest(
    name="column_not_null_test",
    description="Ensure no null values",
    testDefinition="columnValuesToBeNotNull",
    entityLink="<#E::table::service.database.schema.table::columns::column_name>",
    testSuite=test_suite.fullyQualifiedName,
    parameterValues=[]
))
```

## Create Lineage

```python
from metadata.generated.schema.api.lineage.addLineage import AddLineageRequest
from metadata.generated.schema.type.entityLineage import EntitiesEdge
from metadata.generated.schema.type.entityReference import EntityReference

lineage = AddLineageRequest(
    edge=EntitiesEdge(
        fromEntity=EntityReference(id=source_table.id, type="table"),
        toEntity=EntityReference(id=target_table.id, type="table"),
    )
)
metadata.add_lineage(lineage)
```

## Search Entities

```python
results = metadata.es_search_from_fqn(
    entity_type=Table,
    fqn_search_string="*sales*",
    size=100
)
```
