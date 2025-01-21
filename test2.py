import requests
 
# ERP Credentials
BASE_URL = "https://demoerp.enkinext.com"
ERP_USER = "Administrator"
ERP_PASS = "Test#1212$"
 
# Function to login to ERPNext
def login_to_erp(base_url, user, password):
    session = requests.Session()
    login_url = f"{base_url}/api/method/login"
    login_payload = {"usr": user, "pwd": password}
    response = session.post(login_url, data=login_payload)
    if response.status_code == 200:
        print("Login successful!")
        return session
    else:
        print("Login failed:", response.text)
        return None
 
# Fetch all Stock Reconciliation documents and their items
def fetch_stock_reconciliation_items(session, base_url):
    # Fetch all reconciliation document names
    # demoerp.enkinext.com/api/resource/Payment Entry
    # https://demoerp.enkinext.com/api/resource/Payment%20Entry/ACC-PAY-2025-00016
    payment_url = f"{base_url}/api/resource/Payment Entry?limit=1000"
    response = session.get(payment_url)
    if response.status_code == 200:
        reconciliations = response.json().get("data", [])
        all_items = []
       
        # Iterate over each reconciliation to fetch items
        for reconciliation in reconciliations:
            reconciliation_name = reconciliation["name"]
            
            doc_url = f"{base_url}/api/resource/Payment Entry/{reconciliation_name}"
            doc_response = session.get(doc_url)
            
            # print('response is',doc_response)
            if doc_response.status_code == 200:
                doc_data = doc_response.json()
                doc_response_array=[]
                doc_response_array.append(doc_data.get("data", []))
                # print('array data',doc_response_array)
                # title= doc_data.get('title',None)
                # print('title name is',title)
                # print('response data is',doc_data)
                # items = doc_data.get("references", [])
               
               
                for item in doc_response_array:
                    all_items.append({
                        "title": item.get("title"),
                        "references": item.get("references"),
                        # "qty": item.get("qty"),
                        # "warehouse": item.get("warehouse"),  # Fetching warehouse details
                    })
            else:
                print(f"Failed to fetch details for {reconciliation_name}: {doc_response.text}")
       
        return all_items
    else:
        print("Failed to fetch Stock Reconciliation documents:", response.text)
        return []
 
# Main script
session = login_to_erp(BASE_URL, ERP_USER, ERP_PASS)
if session:
    all_items = fetch_stock_reconciliation_items(session, BASE_URL)
    if all_items:
        print(f"Total items fetched: {len(all_items)}")
        for item in all_items:
            data=[]
            title=item.get("title",[])
            data.append(title)
            references = item.get("references", [])
            for ref in references:
                reference=[]
                reference.append(ref.get("outstanding_amount"))
                data.append(reference)

            
            print(data) 
    else:
        print("No items found in Stock Reconciliation.")
 