import xmlrpc.client
import requests
from google.cloud import storage
import os
import csv
import json

# Odoo connection setup
url = 'http://localhost:8010'
db = 'simstage1'
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

# Function to read CSV files and print data in sequence
def read_all_csvs(csv_directory):
    if not os.path.exists(csv_directory):
        print(f"⚠️ Directory '{csv_directory}' does not exist.", flush=True)
        return {}

    csv_files = [f for f in os.listdir(csv_directory) if f.endswith('.csv')]
    file_count = len(csv_files)

    print(f"\n📁 Total CSV files found: {file_count}", flush=True)
    csv_json_data = {}

    for i in range(file_count):
        filename = csv_files[i]
        file_path = os.path.join(csv_directory, filename)
        try:
            with open(file_path, mode='r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                data = [row for row in reader]

                print(f"\n📄 [{i+1}/{file_count}] File: {filename}", flush=True)
                print(json.dumps(data, indent=4), flush=True)
                print("\n" + "=" * 60 + "\n", flush=True)

                csv_json_data[filename] = data
        except Exception as e:
            print(f"⚠️ Error reading {filename}: {e}", flush=True)

    return csv_json_data

# Execute
csv_data_as_json = read_all_csvs(csv_directory)

# Optional: Print combined data at the end
print("\n📦 Combined Data from All Files:", flush=True)
print(json.dumps(csv_data_as_json, indent=4), flush=True)

# Now update cert_link field using CertiWebLink
fields_to_update = [
    "treatment", "disc_perc", "crown_height", "girdle", "girdle_thin", "girdle_perc", "girdle_condition",
    "culet_size", "culet_condition", "fluorescence_color", "fancy_color", "fancy_intensity", "fancy_overtone",
    "pair_stock_ref", "is_matched_pair_separable", "length", "width", "height", "cert_issue_date", "star_length",
    "web_link", "laser_inscription", "lower_half", "member_comment", "handa", "cash_disc_price",
    "milky", "enhancements", "city", "origin", "cash_disc_perc", "black_inclusion", "identification_marks", "state",
    "for_trade_show", "last_customer", "stone_location", "not_for_web", "t2a", "dept_code"
]

def to_camel_case(word_str):
    parts = word_str.split('_')
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])

def to_pascal_case(word_str):
    return ''.join(word.capitalize() for word in word_str.split('_'))

def to_capital_words(word_str):
    return ' '.join(word.capitalize() for word in word_str.split('_'))

for filename, records in csv_data_as_json.items():
    print(f"\n🔄 Updating records from file: {filename}", flush=True)
    for record in records:
        cert_no = record.get('certiNo')

        if not cert_no:
            print(f"⚠️ Skipping record with missing CertificateNo: {record}", flush=True)
            continue

        try:
            # Find the record in Odoo
            pricing_ids = models.execute_kw(
                db, uid, password,
                model_name, 'search',
                [[['certificate_no', '=', cert_no]]]
            )

            if pricing_ids:
                # Prepare values to update
                update_values = {}
                for field in fields_to_update:
                    camel = to_camel_case(field)
                    pascal = to_pascal_case(field)
                    capital = to_capital_words(field)
                    value = record.get(camel) or record.get(pascal) or record.get(capital)
                    update_values[field] = value or False  # Set to False (null in Odoo) if not provided

                models.execute_kw(
                    db, uid, password,
                    model_name, 'write',
                    [pricing_ids, update_values]
                )
                print(f"✅ Updated fields for CertificateNo {cert_no}", flush=True)
            else:
                print(f"❌ No matching inventory.pricing record found for CertificateNo {cert_no}", flush=True)

        except Exception as e:
            print(f"⚠️ Error updating CertificateNo {cert_no}: {e}", flush=True)
