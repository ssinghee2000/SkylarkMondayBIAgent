import re

def apply_sector_filter(data,sector): #gets the rows of data only for a particular sector
    if not sector:
        return data
    sector=sector.lower()
    return[d for d in data if sector in str(d.get("sector","")).lower()]

def count_records(data):# gets number of records in a data
    return len(data)

def clean_currency(value):# A column may have values like $12k or 12,000 - so its important that these values are treated as numbers and not characters
    if not value:
        return 0
    value=str(value).lower()
    if "k" in value:
        try:
            return float(value.replace("k",""))*1000
        except:
            pass
    value=re.sub(r"[^\d.]","",value)
    try:
        return float(value)
    except:
        return 0

def calculate_pipeline_value(deals):#it takes the dataset under consideration and calculate total value for a particular deal
    total=0
    for deal in deals:
        total+=clean_currency(deal.get("deal_value"))
    return total

def summarize_data(data):
    summary={"total_records":len(data)}
    sector_counts={}
    for d in data:
        sector=d.get("sector") or "Unknown"
        sector_counts[sector]=sector_counts.get(sector,0)+1
    summary["sector_breakdown"]=sector_counts
    return summary

def detect_data_quality_issues(data):#keeps a check on  data quality, how many missing values across different columns
    issues=[]
    missing_sector=0
    missing_value=0
    missing_stage=0
    for d in data:
        if not d.get("sector"):
            missing_sector+=1
        if not d.get("deal_value"):
            missing_value+=1
        if not d.get("deal_stage"):
            missing_stage+=1
    if missing_sector>0:
        issues.append(f"{missing_sector} records missing sector information")
    if missing_value>0:
        issues.append(f"{missing_value} records missing deal value")
    if missing_stage>0:
        issues.append(f"{missing_stage} records missing deal stage")
    if not issues:
        issues.append("No major data quality issues detected")
    return issues

def pipeline_metrics(deals):
    sector_counts={}
    total=len(deals)
    for d in deals:
        sector=d.get("sector") or "Unknown"
        sector_counts[sector]=sector_counts.get(sector,0)+1
    return{"total_deals":total,"sector_distribution":sector_counts}


def pipeline_value_metrics(deals):
    total_value=0
    for d in deals:
        total_value+=clean_currency(d.get("deal_value"))
    return{"pipeline_value":total_value}


def execution_metrics(work_orders):
    sector_counts={}
    total=len(work_orders)
    for w in work_orders:
        sector=w.get("sector") or "Unknown"
        sector_counts[sector]=sector_counts.get(sector,0)+1
    return{"active_work_orders":total,"sector_distribution":sector_counts}


def revenue_metrics(work_orders):
    billed=0
    collected=0
    receivable=0
    for w in work_orders:
        billed+=clean_currency(w.get("billed_value"))
        collected+=clean_currency(w.get("collected_value"))
        receivable+=clean_currency(w.get("receivable_value"))
    return{
        "total_billed":billed,
        "total_collected":collected,
        "total_receivable":receivable
    }


def sector_dependency_metrics(sector_distribution):
    total=sum(sector_distribution.values())
    percentages={}
    if total==0:
        return percentages
    for sector,count in sector_distribution.items():
        percentages[sector]=round((count/total)*100,2)
    return percentages


def data_quality_summary(data,fields):
    missing_counts={}
    for field in fields:
        missing=0
        for row in data:
            if not row.get(field):
                missing+=1
        missing_counts[field]=missing
    return missing_counts


def compute_all_metrics(deals=None,work_orders=None):

    deals=deals or []
    work_orders=work_orders or []

    metrics={}

    if deals:
        pipeline=pipeline_metrics(deals)
        metrics["pipeline"]=pipeline
        metrics["pipeline_value"]=pipeline_value_metrics(deals)
        metrics["pipeline_sector_dependency"]=sector_dependency_metrics(
            pipeline["sector_distribution"]
        )
        metrics["deal_data_quality"]=data_quality_summary(
            deals,["deal_value","deal_stage","sector"]
        )

    if work_orders:
        execution=execution_metrics(work_orders)
        metrics["execution"]=execution
        metrics["revenue"]=revenue_metrics(work_orders)
        metrics["work_order_sector_dependency"]=sector_dependency_metrics(
            execution["sector_distribution"]
        )
        metrics["work_order_data_quality"]=data_quality_summary(
            work_orders,["contract_value","billed_value","collected_value","sector"]
        )

    return metrics