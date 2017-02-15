# coding: utf-8
import boto3
import email
import json
import logging
import os
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def handler(event, context):
    logger.info("Collecting event record data...")
    record = event["Records"][0]
    try:
        logger.info("Looking for SES event...")
        bucket_name =  os.environ['SESACMS3BucketName']
        message_id =  record["ses"]["mail"]["messageId"]
        message_source =  record["ses"]["mail"]["source"]
        message_destination =  record["ses"]["mail"]["destination"]
    except KeyError:
        logger.critical("There was a problem retrieving data "
                        "from the event record, {}".format(record))
        return("FAIL")

    s3_client = boto3.client('s3')
    logger.info("Fetching s3 object: {}/{}".format(bucket_name, message_id))
    mail_object = s3_client.get_object(Bucket = bucket_name, Key = message_id)
    logger.info("Decoding mail body...")
    email_data = mail_object["Body"].read().decode('utf-8')
        
    # Get env variables
    # We need to use a verified email address rather than relying on the source
    logger.info("Retrieving environment settings...")
    email_from = os.environ['FromAddress']
    filter_addresses = [address.strip() for address in os.environ['FilterAddresses'].split(",")]
    forwarding_addresses = [address.strip() for address in os.environ['ForwardingAddresses'].split(",")]
    # Filter out addresses
    filtered_addresses = [address for address in message_destination if address in filter_addresses]
    
    if len(filtered_addresses) == 0:
        logger.debug("No filtering addresses found, skipping message...")
        return ("CONTINUE")    
    logger.info("Found filtering addresses {}, "
                "forwarding the message...".format(','.join(filtered_addresses)))

    email_object = email.message_from_string(email_data)
    email_subject = email_object.get('Subject', 'Verification message for ACM')
    logger.info("Parsing mail: {}".format(email_subject))
    email_text=""

    for part in email_object.walk():
        c_type = part.get_content_type()
        c_disp = part.get('Content-Disposition')
        if c_type == 'text/plain' and c_disp == None:
            email_text = email_text + '\n' + part.get_payload()
        else:
            continue
    logger.info("Connecting to SES client")
    ses_client = boto3.client('ses')
    response = ses_client.send_email(
        Source=email_from,
        Destination={
            'ToAddresses': forwarding_addresses
        },
        Message={
            'Subject': {
                'Data': email_subject,
            },
            'Body': {
                'Text': {
                    'Data': email_text,
                }
            }
        },
        Tags=[
            {
                'Name': 'string',
                'Value': 'string'
            },
        ],
    )
    logger.info("Sent verification email successfully to {}".format(','.join(forwarding_addresses)))

    return "CONTINUE"