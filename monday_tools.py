import requests
import os
import streamlit as st
URL = "https://api.monday.com/v2"
headers = {
    "Authorization": st.secrets("MONDAY_API_KEY")
}
deals_board_id = 5026984341
work_orders_board_id = 5026984324

def fetch_board(board_id):

    query = f"""
    {{
      boards(ids: {board_id}) {{
        items_page {{
          items {{
            name
            column_values {{
              column {{
                title
              }}
              text
            }}
          }}
        }}
      }}
    }}
    """
    response = requests.post(URL, json={"query": query}, headers=headers)
    data = response.json()
    items = data["data"]["boards"][0]["items_page"]["items"]
    # print(items)
    return items

def get_deals():

    items = fetch_board(deals_board_id)
    deals = []
    for item in items:
        deal = {"name": item["name"]}
        for col in item["column_values"]:
            deal[col["column"]["title"]] = col["text"]
        deals.append(deal)
    return deals

# fetch_board(deals_board_id)
# get_deals()

def get_work_orders():
    work_board = fetch_board(work_orders_board_id)
    orders = []
    for work in work_board:
        order = {"name":work["name"]}
        for col in work['column_values']:
            order[col['column']['title']] = col['text']
        orders.append(order)
    
    return orders
            


