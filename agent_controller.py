from llm_agent import ask_llm
from monday_tools import get_deals, get_work_orders

import json
from analytics_tools import compute_all_metrics,apply_sector_filter,count_records,calculate_pipeline_value,summarize_data,detect_data_quality_issues

def extract_plan(user_query): #from input query you extract the intent of the query, like which dataset is required for the particular query, 
    #if there any specific metric the user is looking for, or if the sector is mentioned then extract that as well
    planning_prompt = f"""
    You are helping decide which dataset is needed.

    User question:
    {user_query}
    Decide what operations are needed.

    Return JSON with:
    dataset: deals | work_orders | both
    operation: count | pipeline_value | summary
    filters: sector or null

    Do not include explanations or markdown.
    ------------------------------------------------------------------------
    Example
    ------------------------------------------------------------------------
    Query 1:
    How many work orders are there?
    Output:
    `{{
    "dataset": "work_orders",
    "operation": "count",
    "filters": null
    }}`

    Query2:
    How's our pipeline looking for energy sector?
    Output:
    `{{
    "dataset": "deals",
    "operation": "pipeline_value",
    "filters": "energy"
    }}`"""


    response = ask_llm([
        {"role": "user", "content": planning_prompt} # this returns the JSON format output which gets parsed to json.loads in 'plan'
    ])

    try:
        plan = json.loads(response)

    except:

        query_lower = user_query.lower()

        if "work order" in query_lower:
            dataset = "work_orders"
        elif "deal" in query_lower or "pipeline" in query_lower:
            dataset = "deals"
        else:
            dataset = "both"

        plan = {
            "dataset": dataset,
            "operation": "summary",
            "filters": None
        }

    return plan
## the schemas are required for standardizing column headers for deals and work orders
DEALS_SCHEMA_MAP = {
    "Deal Name": "deal_name",
    "Owner code": "owner_code",
    "Client Code": "client_code",
    "Deal Status": "deal_status",
    "Close Date (A)": "close_date",
    "Closure Probability": "closure_probability",
    "Masked Deal value": "deal_value",
    "Tentative Close Date": "tentative_close_date",
    "Deal Stage": "deal_stage",
    "Product deal": "product",
    "Sector/service": "sector",
    "Created Date": "created_date"
}
WORK_ORDER_SCHEMA_MAP={
"Deal name masked":"deal_name",
"Customer Name Code":"customer_code",
"Serial #":"serial_number",
"Nature of Work":"nature_of_work",
"Execution Status":"execution_status",
"Sector":"sector",
"Type of Work":"work_type",
"Probable Start Date":"start_date",
"Probable End Date":"end_date",
"Amount in Rupees (Excl of GST) (Masked)":"contract_value",
"Billed Value in Rupees (Excl of GST.) (Masked)":"billed_value",
"Collected Amount in Rupees (Incl of GST.) (Masked)":"collected_value",
"Amount Receivable (Masked)":"receivable_value",
"Invoice Status":"invoice_status",
"Collection status":"collection_status",
"Billing Status":"billing_status"
}

def normalize_work_orders_schema(work_orders):
    normalized=[]
    for order in work_orders:
        clean_record={}
        for key,value in order.items():
            if key in WORK_ORDER_SCHEMA_MAP:
                clean_key=WORK_ORDER_SCHEMA_MAP[key]
            else:
                clean_key=key.lower().replace(" ","_")
            clean_record[clean_key]=value
        normalized.append(clean_record)
    return normalized

def normalize_deals_schema(deals):
    normalized = []
    for deal in deals:
        clean_record = {}
        for key, value in deal.items():
            if key in DEALS_SCHEMA_MAP:
                clean_key = DEALS_SCHEMA_MAP[key]
            else:
                clean_key = key.lower().replace(" ", "_")
            clean_record[clean_key] = value
        normalized.append(clean_record)
    return normalized

def run_agent(user_query,actions):
    plan=extract_plan(user_query) # gets the dictionary with dataset,operation and filters/sectors as keys
    dataset=plan["dataset"]
    operation=plan["operation"]
    sector=plan["filters"]
    dataset=dataset.lower().strip()

    data={}

    # Step 1 — fetch monday data
    if dataset in ["deals","both"]:
        actions.append("Querying Monday API → Deals board")
        deals=get_deals()
        deals=normalize_deals_schema(deals)#cleaning data for deals
        data["deals"]=deals
        actions.append(f"Retrieved {len(deals)} deals")

    if dataset in ["work_orders","both"]:
        actions.append("Querying Monday API → Work Orders board")
        orders=get_work_orders()
        orders=normalize_work_orders_schema(orders)#cleaning data for work orders
        data["work_orders"]=orders
        actions.append(f"Retrieved {len(orders)} work orders")

    # Step 2 — compute BI metrics on full dataset
    actions.append("Computing business metrics")

    metrics=compute_all_metrics(
        deals=data.get("deals"),
        work_orders=data.get("work_orders")
    )

    # Step 3 — optional filtered view (for specific questions)
    filtered_data={}

    if sector and "deals" in data:
        actions.append(f"Filtering sector view: {sector}")
        filtered_data["deals"]=apply_sector_filter(data["deals"],sector)

    if sector and "work_orders" in data:
        filtered_data["work_orders"]=apply_sector_filter(data["work_orders"],sector)

    # Step 4 — LLM explanation
    analysis_prompt=f"""
You are a business intelligence analyst preparing insights for company leadership.

User question:
{user_query}

Business metrics computed from company data:
{metrics}

Filtered sector view (if relevant):
{filtered_data}

Instructions:

1. Base your analysis ONLY on the provided metrics.
2. Do not invent numbers.
3. Percentages and sector comparisons must refer to the full dataset unless explicitly stated.
4. Focus on insights relevant to leadership decisions.

Write the response using this structure:

Executive Summary
Provide a direct answer to the user's question.

Operational Metrics
Highlight the key numbers from the metrics.

Strategic Insight
Explain what these numbers imply for the business.


Keep the response concise and leadership-focused.
"""

    actions.append("Generating leadership insights")

    response=ask_llm([
        {"role":"user","content":analysis_prompt}
    ])

    return response





# def run_agent(user_query,actions):

#     plan=extract_plan(user_query)
#     dataset=plan["dataset"]
#     operation=plan["operation"]
#     sector=plan["filters"]
#     dataset=dataset.lower().strip()

#     data={}
#     summary={}

#         # Step 1 — fetch monday data
#     if dataset in ["deals","both"]:
#         actions.append("Querying Monday API → Deals board")
#         deals=get_deals()
#         deals=normalize_deals_schema(deals)
#         data["deals"]=deals
#         actions.append(f"Retrieved {len(deals)} deals")

#     if dataset in ["work_orders","both"]:
#         actions.append("Querying Monday API → Work Orders board")
#         orders=get_work_orders()
#         orders=normalize_work_orders_schema(orders)
#         data["work_orders"]=orders
#         actions.append(f"Retrieved {len(orders)} work orders")

#     # Step 2 — apply filters
#     if sector and "deals" in data:
#         actions.append(f"Filtering sector: {sector}")
#         data["deals"]=apply_sector_filter(data["deals"],sector)

#     # Step 3 — analytics operations
#     if operation=="count":

#         if "deals" in data:
#             summary["deal_count"]=count_records(data["deals"])

#         if "work_orders" in data:
#             summary["work_order_count"]=count_records(data["work_orders"])

#     elif operation=="pipeline_value" and "deals" in data:

#         actions.append("Calculating pipeline value")
#         summary["pipeline_value"]=calculate_pipeline_value(data["deals"])
#         summary["deal_count"]=count_records(data["deals"])

#     else:

#         if "deals" in data:
#             summary["deal_summary"]=summarize_data(data["deals"])

#         if "work_orders" in data:
#             summary["work_order_summary"]=summarize_data(data["work_orders"])

#     # Step 4 — detect data issues
#     issues=[]

#     if "deals" in data:
#         issues.extend(detect_data_quality_issues(data["deals"]))

#     if "work_orders" in data:
#         issues.extend(detect_data_quality_issues(data["work_orders"]))

#     summary["data_quality_issues"]=issues

#     metrics=compute_all_metrics(
#     deals=data.get("deals"),
#     work_orders=data.get("work_orders")
#     )
#     # Step 5 — LLM explanation
#     analysis_prompt=f"""
#     You are a business intelligence analyst preparing insights for company leadership.
#     User question:
#     {user_query}

#     Structured metrics computed from the data:
#     {summary}

#     Important instructions:

#     1. Base your analysis ONLY on the provided metrics.
#     2. Do not invent numbers or assumptions.
#     3. Avoid misleading statistics (for example, percentages based only on filtered subsets).
#     4. Focus on decision-relevant insights for leadership.

#     Write the response using this structure:

#     Executive Summary
#     Provide a short direct answer to the user's question.

#     Operational Metrics
#     List the key numbers that support the answer.

#     Strategic Insight
#     Explain what these numbers imply for the business.

#     Risks or Data Limitations
#     Mention missing or unreliable fields if they affect interpretation.
     
#     Keep the response concise and leadership-focused.

# """

#     actions.append("Generating business insights")
#     response=ask_llm([
#         {"role":"user","content":analysis_prompt}
#     ])

#     return response