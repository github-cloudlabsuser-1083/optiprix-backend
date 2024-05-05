import os
import pandas as pd

from openai import AzureOpenAI

from generate_prompt import get_prompt

api_key = os.getenv('API_KEY')
api_version = os.getenv('API_VERSION')
azure_endpoint = os.getenv('AZURE_ENDPOINT')

# Initialize the AzureOpenAI client
client=AzureOpenAI(api_key=api_key, api_version=api_version, azure_endpoint=azure_endpoint)

# Function to get rows from the dataset based on the product_id
def get_rows(product_id, dataset_url):
    df = pd.read_csv(dataset_url)
    # get rows where product_id column matches the product_id, but return all the rows in the format bed1,col2,col3,... replacing col2, col3, ... with the actual column values. 
    rows = df[df['product_id'] == product_id]
    rows_str = ''
    # Take the first row in df and join it with commas to get the column names e.g. add product_id,product_category_name,month_year,qty,total_price,freight_price,unit_price,product_name_lenght,product_description_lenght,product_photos_qty,product_weight_g,product_score,customers,weekday,weekend,holiday,month,year,s,volume,comp_1,ps1,fp1,comp_2,ps2,fp2,comp_3,ps3,fp3,lag_price\n
    rows_str += ','.join(df.columns) + '\n'
    for i, row in rows.iterrows():
        row_str = ','.join([str(x) for x in row.values])
        rows_str += row_str + '\n'
    return rows_str

def get_info(product_id, dataset):
    df = pd.read_csv(dataset)
    
    # get all the rows where product_id matches the product_id and return the month_year and unit_price columns
    rows = df[df['product_id'] == product_id]
    # join by comma (csv format) and return the rows
    rows_dict = []
    
    cur_index = 0
    for i, row in rows.iterrows():
        row_obj = {
            'month_year': row['month_year'][3:10],
            'unit_price': row['unit_price']
        }
        
        # add the row_obj to the rows_dict
        rows_dict.append(row_obj)
        cur_index += 1
                
    return rows_dict

def generate_prompt(product_id, field, value, dataset):
    rows = get_rows(product_id, dataset_url=dataset['url'])
    prompt = get_prompt(product_id, field, value, rows)
    
    messages = client.chat.completions.create(
        model=os.getenv('DEPLOYMENT_NAME'),
        messages=[
            {
                "role": "system",
                "content": prompt
            }
        ]
    )
    
    return messages.choices[0].message.content
