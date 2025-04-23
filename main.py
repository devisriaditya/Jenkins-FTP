import xmlrpc.client
import os
import requests
from google.cloud import storage

# Odoo connection setup
url = 'http://localhost:8010'
db = 'simstage1'
# url = 'https://erp-stage1.simstar.co/'
# db = 'simstar-stage-1-18787506'
username = 'admin'
password = '12345'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Check if the model 'inventory.pricing' exists
model_name = 'inventory.pricing'

model_exists = models.execute_kw(
    db, uid, password,
    'ir.model', 'search_count',
    [[['model', '=', model_name]]]
)

if model_exists:
    print(f"Model '{model_name}' exists.")
else:
    print(f"Model '{model_name}' does NOT exist.")

