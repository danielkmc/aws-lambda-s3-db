import json
import urllib.parse
import boto3
import datetime
import re
import string

print('Loading function')

s3 = boto3.client('s3')
file = ""
date = datetime.time
new_date = False
dcl = ['ALTER', 'CREATE', 'DROP']

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        print("CONTENT TYPE: " + response['ContentType'])
        download_path = '/tmp/' + key
        s3.download_file(bucket, key, download_path)
        global file
        file = open(download_path, 'r')
        starter()
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e


def starter():
    output_name = file.name.find('/tmp/')
    output_file = open('/tmp/')
    logs = yield_matches(file)
    index = 1
    for log in logs:
        login_info, log_stuff = _parser(log)
        print(login_info, '\n', log_stuff, '\n', date)
        for word
        
    output_file.close()
    s3.upload_file(output_name[5:], bucket_name, output_name[5:])

def _parser(data=""):
    """function used after distinguishing individual log entries

        Takes data passed to it and retrieves the date, user info, and log keywords"""

    if data == "":
        pass
    
    """Retrieve timestamp"""
    validate(data[:25])
    """retrieve log data"""
    log_data = re.findall(r"[\w]+", data)
    """Retrieve user info"""
    login_info = [log_data[i] for i in (7, 9, 11, 13, 15)]

    
    return login_info, log_data


def validate(date_text):
    try:
        global date, new_date
        date = datetime.datetime.strptime(date_text, '\'%Y-%m-%dT%H:%M:%SZ UTC')
        return True
    except ValueError:
        date = datetime.time
        return False


def yield_matches(f):
    log = []
    for line in f:
        if validate(line[:25]):
            if len(log) > 0:
                yield "".join(log)
                log = []

        log.append(line)

    yield "".join(log)


