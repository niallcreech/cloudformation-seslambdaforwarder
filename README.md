SESLambdaForwarder cloudformation stack
=======================================

SESLambdaForwarder is a short AWS Cloudformation template for creating an AWS Lambda function that reads and forwards mail from its own S3 bucket. This is useful for setting up mail forwarding on AWS Simple Email Service (SES)

Using the SESLambdaForwarder cloudformation stack
-------------------------------------------------
					
When creating this stack you can set the email addresses to forward, and a set of forwarding addresses. This cloudformation sets up a lambda function and a S3 bucket with default 3 day deletion policy. We need to setup SES on the domain we want to receive mail on since it doesnt have cloudformation support, but luckily this is straightforward.
					
Setup SES on the mail domain
---------------------------
							
* Create an SES domain for the base domain name superdomain.com
* Let the SES domain creation set route 53 entries for verification and MX, eg in the superdomain.com hosted zone, superdomain . com MX 10 inbound−smtp . eu−west−1.amazonaws . com	
* Create a SES rule et to send emails to the S3 bucket.		
* When creating certificates, use superdomain.com as the validation domain, this means admin@superdomain.com will be emailed when we create any sub-domain something.somewhere.superdomain.com
* While the stack requiring an ACM SSL certificate is being created, the forwarding addresses should all receive a validation email 

