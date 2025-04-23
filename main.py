import xmlrpc.client
import requests
from google.cloud import storage
import os
import csv
import json

# Odoo connection setup
url = 'http://localhost:8010'
db = 'simstage1'
# url = 'https://erp-stage1.simstar.co/'
# db = 'simstar-stage-1-18787506'
username = 'admin'
password = '12345'

print("Authenticating with Odoo...", flush=True)
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

if not uid:
    print("❌ Authentication failed. Check your credentials or Odoo server connection.", flush=True)
    exit()

print(f"✅ Authenticated with UID: {uid}", flush=True)

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Check if the model 'inventory.pricing' exists
model_name = 'inventory.pricing'

try:
    print(f"Checking if model '{model_name}' exists...", flush=True)
    model_exists = models.execute_kw(
        db, uid, password,
        'ir.model', 'search_count',
        [[['model', '=', model_name]]]
    )

    if model_exists:
        print(f"✅ Model '{model_name}' exists.", flush=True)
    else:
        print(f"❌ Model '{model_name}' does NOT exist.", flush=True)
except Exception as e:
    print(f"⚠️ Error while checking model: {e}", flush=True)
    exit()

# Directory where CSV files are located
csv_directory = './static'  # Change this to your actual path

# Function to read CSV files and print file name + data as JSON
def read_csvs_and_print_json(csv_directory):
    csv_json_data = {}

    if not os.path.exists(csv_directory):
        print(f"⚠️ Directory '{csv_directory}' not found.", flush=True)
        return csv_json_data

    for filename in os.listdir(csv_directory):
        if filename.endswith('.csv'):
            file_path = os.path.join(csv_directory, filename)
            try:
                with open(file_path, mode='r', encoding='utf-8-sig') as file:
                    reader = csv.DictReader(file)
                    data = [row for row in reader]

                    print(f"\n📄 File: {filename}", flush=True)
                    print(json.dumps(data, indent=4), flush=True)
                    print("\n" + "=" * 60 + "\n", flush=True)

                    csv_json_data[filename] = data
            except Exception as e:
                print(f"⚠️ Error reading {filename}: {e}", flush=True)

    return csv_json_data

# Read and print CSVs
csv_data_as_json = read_csvs_and_print_json(csv_directory)

# Optionally print all collected data at the end
print("\n📦 All CSV Data Combined:", flush=True)
print(json.dumps(csv_data_as_json, indent=4), flush=True)
