import dotenv
import json

import pandas as pd
from flask import Flask, render_template, request, send_from_directory
from flask_cors import CORS

from ai import generate_prompt, get_info

dotenv.load_dotenv()

# Load the dataset
available_datasets = []
with open('available_datasets.json') as f:
    available_datasets = json.load(f)

# User inputs for product ID, field, and value
app = Flask(__name__)
CORS(app)

FLUTTER_WEB_APP = 'templates'

@app.route('/')
def render_page():
    return render_template('index.html')


@app.route('/web/')
def render_page_web():
    return render_template('index.html')


@app.route('/web/<path:name>')
def return_flutter_doc(name):

    datalist = str(name).split('/')
    DIR_NAME = FLUTTER_WEB_APP

    if len(datalist) > 1:
        for i in range(0, len(datalist) - 1):
            DIR_NAME += '/' + datalist[i]

    return send_from_directory(DIR_NAME, datalist[-1])

@app.route('/api/list_products/<dataset_name>')
def list_products(dataset_name):
    dataset = next((ds for ds in available_datasets if ds['name'] == dataset_name), None)
    if dataset is None:
        return "Dataset not found", 404
    df = pd.read_csv(dataset['url'])
    # Get unique product IDs
    product_ids = df['product_id'].unique()
    return list(product_ids)

@app.route('/api/available_datasets')
def available_datasets_f():
    return available_datasets

@app.route('/api/<product_id>/<field>/<value>')
def optimize_price(product_id, field, value):
    if not product_id:
        return "Product ID not provided", 400
    if not field:
        return "Field not provided", 400
    if not value:
        return "Value not provided", 400
    if not request.args.get('dataset'):
        return "Dataset not provided", 400
    
    dataset = next((ds for ds in available_datasets if ds['name'] == request.args.get('dataset')), None)
    if dataset is None:
        return "Dataset not found", 404
    prompt = generate_prompt(product_id, field, value,dataset)
    try: 
        json.loads(prompt)
    except json.JSONDecodeError:
        return prompt
    
    return json.loads(prompt)

@app.route('/api/product_history/<product_id>')
def product_history(product_id):
    if not product_id:
        return "Product ID not provided", 400
    if not request.args.get('dataset'):
        return "Dataset not provided", 400
    
    dataset = next((ds for ds in available_datasets if ds['name'] == request.args.get('dataset')), None)
    
    return get_info(product_id, dataset['url'])