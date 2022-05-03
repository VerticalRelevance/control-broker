import json

import boto3
from botocore.exceptions import ClientError

s3 = boto3.client('s3')

def s3_select_to_file(
    bucket,
    key,
    expression,
    outfile
):
    
    print(f'select_object_content\nbucket:\n{bucket}\nkey:\n{key}')

    try:
        r = s3.select_object_content(
            Bucket=bucket,
            Key=key,
            Expression=expression,
            ExpressionType='SQL',
            InputSerialization={
                'JSON': {
                    'Type': 'DOCUMENT'
                },
            },
            OutputSerialization={
                'JSON': {
                    'RecordDelimiter': '\n'
                }
            }
        )
    except ClientError as e:
        print(f'ClientError:\n{e}')
        raise
    else:
        event_stream = r['Payload']
        end_event_received = False
        with open(outfile, 'wb') as f:
            # Iterate over events in the event stream as they come
            for event in event_stream:
                # If we received a records event, write the data to a file
                if 'Records' in event:
                    data = event['Records']['Payload']
                    f.write(data)
                # If we received a progress event, print the details
                elif 'Progress' in event:
                    print(event['Progress']['Details'])
                # End event indicates that the request finished successfully
                elif 'End' in event:
                    print('Result is complete')
                    end_event_received = True
        if not end_event_received:
            raise Exception("End event not received, request incomplete.")

def s3_uri_to_bucket_key(*,Uri):
    path_parts=Uri.replace("s3://","").split("/")
    bucket=path_parts.pop(0)
    key="/".join(path_parts)
    return bucket, key

def lambda_handler(event,context):
    
    print(event)
    
    select_outfile = '/tmp/selected.json'        
    
    bucket = event.get('Bucket')
    key = event.get('Key')
    
    if not bucket and not key:
        bucket, key = s3_uri_to_bucket_key(Uri=event['S3Uri'])

    s3_select_to_file(
        bucket = bucket,
        key = key,
        expression = event['Expression'],
        outfile = select_outfile
    )
    
    with open(select_outfile,'r') as f:
        selected = json.loads(f.read())
        
        print(f'selected:\n{selected}\n{type(selected)}')
        
        return {
            'Selected': selected
        }