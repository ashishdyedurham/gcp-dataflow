import apache_beam as beam
from google.cloud import bigquery
import logging
import json
from apache_beam.options.pipeline_options import PipelineOptions


# Function to convert BigQuery rows to JSON
def bq_row_to_json(row):
    return json.dumps(dict(row))

# Function to hit API with JSON data
def hit_api(data, api_url):
    logging.info("Processing element: %s", data)
    return data

# Define the pipeline
def run():
    logging.basicConfig(level=logging.INFO)
    options = PipelineOptions(
        temp_location='gs://test_textfile_to_bigquery_files/temp',  # Specify GCS temp location
        # Add other options as needed
    )

    with beam.Pipeline(options=options) as pipeline:
        # List of tables to read
 # SQL query to perform the join across the tables
        query = """
            SELECT e.Id, e.Name AS emp_name, 
                   ARRAY_AGG(STRUCT(a.Address AS address)) AS addresses
            FROM ti-ds-tii-01.test.emp AS e
            LEFT JOIN ti-ds-tii-01.test.Address AS a ON e.Id = a.Id
            GROUP BY e.Id, e.Name
        """

        # Read data from BigQuery using the join query
        joined_data = (
            pipeline
            | 'Read from BigQuery' >> beam.io.ReadFromBigQuery(query=query, use_standard_sql=True)
        )

        # Convert rows to JSON with addresses as JSON array
        json_data = (
            joined_data
            | 'Convert to JSON' >> beam.Map(row_to_json)
        )
        # Hit API with JSON data
        api_url = 'https://www.google.com'
        
        api_response = (json_data | 'Hit API' >> beam.Map(hit_api, api_url=api_url))

def row_to_json(row):
    # Convert the row to a dictionary
    row_dict = dict(row)
    
    # Convert addresses to JSON array
    row_dict['addresses'] = json.dumps(row_dict.pop('addresses', []))
    
    # Convert the dictionary to a JSON string
    return json.dumps(row_dict)


if __name__ == '__main__':
    run()
