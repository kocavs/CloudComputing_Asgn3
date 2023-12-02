import json
import boto3
import requests
from requests_aws4auth import AWS4Auth
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def lambda_handler(event, context):
    # Initialize clients for Lex
    lex_client = boto3.client('lex-runtime', region_name='us-east-1')

    # Extract AWS credentials for signing requests
    username = 'admin'
    password = 'Xhr@200002030717'
    
    # Define Elasticsearch domain
    es_host = 'search-photosv1-rzclcadspe6lrgsf7j4xpf5cie.us-east-1.es.amazonaws.com'
    
    # Extract query parameter
    query_string_parameters = event.get('queryStringParameters')
    q = query_string_parameters.get('q') if query_string_parameters else None
    logger.debug(f'q: {q}')
    
    if q:
        # Send query to Lex for disambiguation
        lex_response = lex_client.post_text(
            botName='SearchBot',
            botAlias='latest',
            userId='user',
            inputText=q
        )

        # Extract keywords if any slots are filled
        keywords = lex_response.get('slots', {})
        filled_keywords = [value for value in keywords.values() if value]
        logger.debug(f'filled_keywords:{filled_keywords}')
        
        if filled_keywords:
            # Construct the search query for Elasticsearch
            query = {
                      "query": {
                        "query_string": {
                          "default_field": "labels",
                          "query": " ".join(filled_keywords)
                        }
                      }
                    }

            # Perform ElasticSearch query using requests
            es_url = f'https://{es_host}/photos/_search'
            response = requests.get(es_url, auth=(username, password), json=query, headers={"Content-Type": "application/json"})

            # Check response from Elasticsearch
            if response.status_code == 200:
                search_results = response.json()
                
                photos_infos = []
                
                for hit in search_results['hits']['hits']:
                    source=hit['_source']
                    url = "https://{}.s3.amazonaws.com/{}".format(source['bucket'], source['objectKey'])
                    photo_info = {
                         'objectKey': source['objectKey'],
                        'bucket': source['bucket'],
                        'createdTimestamp': source['createdTimestamp'],
                        'labels': source['labels'],
                        'url': url
                    }
                    
                    photos_infos.append(photo_info)
                
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'message': 'Query executed successfully.',
                        'results': photos_infos
                    }),
                    'headers': {
                        'Content-Type': 'application/json'
                    }
                }
            else:
                return {
                    'statusCode': response.status_code,
                    'body': json.dumps({
                        'message': 'Error querying Elasticsearch',
                        'error': response.text
                    }),
                    'headers': {
                        'Content-Type': 'application/json'
                    }
                }

        else:
            # Return empty array if no keywords found
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'No keywords found.',
                    'results': []
                }),
                'headers': {
                    'Content-Type': 'application/json'
                }
            }

    else:
        # Return error if query parameter is missing
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Query parameter missing.'
            }),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
