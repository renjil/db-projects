# Genie Usage Analytics

A comprehensive monitoring solution for tracking usage, engagement, and costs across Databricks AI/BI Genie Spaces.

## Overview

This project provides:
- **Data Ingestion Notebook** (`genie_metrics.py`) - Collects data from Databricks Genie APIs
- **Analytics Dashboard** (`Genie Usage Analytics.lvdash.json`) - Visualizes usage metrics and billing

## Features

### Usage Metrics
- Total Genie Spaces count
- Spaces created and cloned (last 7 days)
- Daily active users (DAU)
- New users and power users tracking
- Conversation trends over time
- Messages per conversation analysis
- Peak usage hours distribution

### Engagement Metrics
- Conversation ratings (thumbs up/down feedback)
- User review submissions
- Top users by conversation count
- Most popular spaces by unique users

### Billing Metrics
- SQL warehouse costs per day
- Total cost tracking (30-day window)
- Filter by warehouse

## Data Sources

### Databricks Genie APIs
The notebook collects data from:
- [ListSpaces](https://docs.databricks.com/api/workspace/genie/listspaces) - Genie space details
- [ListConversations](https://docs.databricks.com/api/workspace/genie/listconversations) - Conversations per space
- [ListConversationMessages](https://docs.databricks.com/api/workspace/genie/listconversationmessages) - Messages per conversation

### System Tables
The dashboard also uses:
- `system.access.audit` - Audit events for Genie (feedback, space creation, cloning)
- `system.billing.usage` - Serverless SQL costs
- `system.compute.warehouses` - Warehouse metadata

## Setup

### Prerequisites
- Databricks workspace with Unity Catalog enabled
- Access to System Tables (billing, audit, compute)
- Databricks SDK (`databricks-sdk>=0.33.0`)

### Configuration

1. **Create the catalog and schema** for storing analytics data:

```python
# The notebook will automatically create these if they don't exist
catalog = "your_catalog"
schema = "genie_analytics"
```

2. **Import the notebook** to your Databricks workspace

3. **Run the notebook** with the following widget parameters:
   - `catalog` - The Unity Catalog to store data
   - `schema` - The schema to store tables

### Tables Created

| Table | Description |
|-------|-------------|
| `genie_spaces` | Space metadata (ID, title, description, warehouse) |
| `genie_conversations` | Conversation records with timestamps |
| `genie_messages` | Individual messages with author details |
| `g_conv_last_90d` | Gold: Conversations by day |
| `g_daily_unique_creators_last_90d` | Gold: Daily unique users |
| `g_top_creators_90d` | Gold: Top users by conversations |
| `g_messages_per_conversation_90d` | Gold: Message counts and duration |
| `g_conversation_hour_hist_90d` | Gold: Peak hours histogram |

## Dashboard Pages

### 1. Usage Analysis
- KPI counters: Total spaces, spaces created/cloned, DAU, new users, power users
- Events per day (create, clone, trash)
- Conversation ratings breakdown
- Most popular spaces table
- Conversations and users over time (line charts)
- Top users bar chart
- Conversation start hour distribution
- Messages per conversation table

### 2. Billing
- Filter by SQL warehouse
- Total cost counter (30 days)
- Daily cost trend (bar chart)

## Customization

### Modifying Space Selection
By default, the notebook uses test space IDs. For production:

```python
# Replace this:
space_ids = [
    {"space_id": "01f08d8be94b1fec8bde6037d5eaf022"},
    ...
]

# With this to fetch all spaces:
for s in spaces:  # Use 'spaces' instead of 'space_ids'
```

### Adjusting Time Windows
The gold tables use 90-day and 30-day windows. Modify the SQL queries to adjust:

```sql
WHERE c.created_timestamp >= DATEADD(day, -90, CURRENT_TIMESTAMP())
```

### Rate Limiting
The notebook includes throttling to avoid API rate limits:

```python
THROTTLE_S = 0.15  # Adjust as needed
```

## Scheduling

For continuous monitoring, schedule the notebook to run periodically:
1. Create a Databricks Job
2. Add the notebook as a task
3. Set a schedule (e.g., hourly or daily)
4. Configure widget parameters in the job

## Dashboard Deployment

1. Import the `.lvdash.json` file to your workspace
2. Update dataset queries to point to your catalog/schema
3. Publish the dashboard

## Extending the Solution

### Adding New Metrics
1. Add API calls or SQL queries to the notebook
2. Create new gold tables
3. Add datasets and widgets to the dashboard JSON

### Custom Audit Events
Available Genie audit events:
- `createSpace` - Space creation
- `cloneSpace` - Space cloning
- `trashSpace` - Space deletion
- `updateConversationMessageFeedback` - User ratings
- `createConversationMessageComment` - Review submissions

## Troubleshooting

### API Errors
- Ensure you have permissions to access Genie spaces
- Check that `include_all=true` is set for cross-user conversation access

### Missing System Tables
- Verify Unity Catalog is enabled
- Check that system tables are accessible in your workspace

### Dashboard Data Issues
- Confirm tables exist in the specified catalog/schema
- Verify gold tables are populated after notebook run

## License

Internal use only.

