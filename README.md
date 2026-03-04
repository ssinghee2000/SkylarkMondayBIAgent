
# Monday Business Intelligence Agent

An AI-powered **Business Intelligence agent** that answers leadership-level business questions using **live data from monday.com boards**.  
The system combines **LLM reasoning with a Python analytics layer** to transform operational data into actionable insights.

---

## Overview

Executives often need quick answers such as:

- How strong is our sales pipeline?
- How many projects are currently active?
- How much revenue is still receivable?

This application automates the process by:

1. Interpreting natural language business questions  
2. Fetching live data from monday.com boards  
3. Cleaning and structuring the data  
4. Computing business metrics  
5. Generating leadership-level insights  

---

## Key Features

**Conversational BI Interface**

Users can ask questions like:

```

How many work orders are currently active?
What is the total value of our deal pipeline?
How much revenue is still receivable?

```

---

**Live Monday.com Integration**

The agent retrieves **real-time data** through the monday.com API.

Supported boards:

- Deals (sales pipeline)
- Work Orders (execution and billing)

---

**Data Cleaning & Normalization**

The system standardizes inconsistent fields such as:

```

deal_value
sector
billed_value
collected_value

```

Currency formats and missing values are handled automatically.

---

**Business Analytics Engine**

Instead of relying on the LLM for calculations, the system computes metrics using Python.

Examples:

- Pipeline value
- Active work orders
- Revenue billed / collected / receivable
- Sector distribution
- Data quality indicators

The LLM then converts these metrics into leadership insights.

---

## Architecture

```

User Query
↓
Query Planner (LLM)
↓
Monday API Data Retrieval
↓
Schema Normalization
↓
Data Cleaning
↓
Analytics Engine (Python)
↓
Structured Business Metrics
↓
LLM Insight Generation
↓
Response to User

```

---

## Technology Stack

```

Frontend: Streamlit
LLM: Groq (Llama models)
Data Source: Monday.com API
Analytics Layer: Python

```

---

## Installation

Install dependencies:

```

pip install -r requirements.txt

```

Run the application:

```

streamlit run app.py

```

---

## Environment Setup

The application requires the following API keys:

```

GROQ_API_KEY
MONDAY_API_KEY

```

For local development, create:

```

.streamlit/secrets.toml

```

Example:

```

GROQ_API_KEY="your_key"
MONDAY_API_KEY="your_key"

```

For deployment, add them in **Streamlit Cloud → App Settings → Secrets**.

---

## Example Queries

```

How many work orders are currently active?
What is the value of our deal pipeline?
Which sectors generate the most projects?
How much revenue is still receivable?

```

---

## Design Principle

The system separates **analytics computation from LLM reasoning**:

```

Python → computes business metrics
LLM → explains insights

```

This approach improves reliability and prevents hallucinated calculations.
```
