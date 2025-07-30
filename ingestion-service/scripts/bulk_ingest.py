import csv
import requests
import json

def bulk_ingest(file_path, url):
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # The column names in the CSV file might be different, adjust as needed
            transaction = {
                "user_id": int(row["User"]),
                "card_id": int(row["Card"]),
                "amount": float(row["Amount"]),
                "description": row["Merchant Name"]
            }
            requests.post(url, data=json.dumps(transaction), headers={'Content-Type': 'application/json'})

if __name__ == "__main__":
    # Assuming the service is running locally and the CSV file is named 'transactions.csv'
    bulk_ingest('transactions.csv', 'http://localhost:8000/transactions/')
