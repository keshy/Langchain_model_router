def responder(answer):
    """
    Default callback method for the LLM manifest

    :param answer: JSON response containing the contents of the LLM generated content.
    :type answer: Dict
    :return: Decorated text data with post processing completed.
    """
    if not answer:
        raise ValueError("No response received from LLM for post processing")
    cloud_type = answer.get('cloud_type')
    cloud_type = cloud_type.lower() if cloud_type else None
    account_id = answer.get('account_id')
    # todo
    features = answer.get('features')
    execute_code_inplace = answer.get('exec_code')

    match cloud_type:
        case 'aws':
            code = """
                import sys, time, requests, json, boto3, urllib.parse
                
                # Function to wait till CloudFormation Stack is created
                def wait_till_stack_created(cloud_formation_client, stack_name, state):
                    is_stack_created = False
                    retry_count = 0
                    max_retry_count = 4  # Increase If stack Creation is taking more time
                    status = None
                    while not is_stack_created or retry_count == max_retry_count:
                        if retry_count > max_retry_count:
                            break
                        retry_count = retry_count + 1
                        stack_summary = cloud_formation_client.describe_stacks(StackName=stack_name)
                        status = stack_summary['Stacks'][0]['StackStatus']
                        if status is not None:
                            if state != status:
                                print("Waiting for 30 sec while stack {} is {}".format(stack_name, state))
                                time.sleep(30)
                                continue
                            else:
                                is_stack_created = True
                        print(f"stack status is {status}")
                        return status
                    print(f"final stack status is {status}")
                    return status
                base_url = "https://api.prismacloud.io"
                customerName = None  # optional. customerName which is tenant Name
                username = "<username>"
                password = "<password>"
                # Prerequisite: Obtain an authorization token by Logging In.
                login_url = f"{base_url}/login"
                if customerName is not None:
                    login_payload = json.dumps({
                      "customerName": customerName,
                      "username": username,
                      "password": password
                    })
                else:
                    login_payload = json.dumps({
                        "username": username,
                        "password": password
                    })
                login_headers = {
                  'Content-Type': 'application/json'
                }
                response = requests.request("POST", login_url, headers=login_headers, data=login_payload, verify=False)
                YOUR_TOKEN = response.json()['token']
                # 1. Fetch Supported Features for cloud type and account type
                supported_features_url = f"{base_url}/cas/v1/features/cloud/aws"
                supported_features_payload = json.dumps({
                  "accountType": "account"
                })
                supported_features_headers = {
                  'accept': 'application/json',
                  'content-type': 'application/json',
                  'x-redlock-auth': YOUR_TOKEN
                }
                response = requests.request("POST", supported_features_url, headers=supported_features_headers,
                                            data=supported_features_payload, verify=False)
                features = response.json()['supportedFeatures']
                features.remove('Cloud Visibility Compliance and Governance')  # Remove the default feature
                # 2. Generate AWS CFT and create IAM Role
                cft_template_gen_url = f"{base_url}/cas/v1/aws_template/presigned_url"
                cft_template_gen_payload = json.dumps({
                  "accountId": str({accountId}),
                  "accountType": "account",
                  "features": features
                })
                cft_template_gen_headers = {
                  'accept': 'application/json',
                  'content-type': 'application/json',
                  'x-redlock-auth': YOUR_TOKEN
                }
                response = requests.request("POST", cft_template_gen_url, headers=cft_template_gen_headers
                                            , data=cft_template_gen_payload, verify=False)
                response = response.json()
                createStackLinkWithS3PresignedUrl = response['createStackLinkWithS3PresignedUrl']
                # Extract urldecoded s3 cft link
                s3_presigned_cft_link = urllib.parse.unquote(createStackLinkWithS3PresignedUrl.split("templateURL=")[-1])
                # Initialize boto3 client, Provide aws access key and secret access key for the account to be onboarded
                cloud_formation_client = boto3.client('cloudformation', aws_access_key_id="<aws_access_key_id>",
                                                      aws_secret_access_key="<aws_secret_access_key>")
                stack_name = 'PrismaCloudRole'  # Change if needed
                parameters = [
                    {
                        'ParameterKey': "PrismaCloudRoleName",
                        'ParameterValue': stack_name,
                        'UsePreviousValue': False,
                    }
                ]
                capabilities = ['CAPABILITY_NAMED_IAM']
                create_stack_resp = cloud_formation_client.create_stack(StackName=stack_name, TemplateURL=s3_presigned_cft_link,
                                                                        Parameters=parameters, Capabilities=capabilities)
                # Wait till stack is created.
                sleep_time = 60*2  # Default wait time 2min
                time.sleep(sleep_time)
                stack_state = wait_till_stack_created(cloud_formation_client, stack_name, "CREATE_COMPLETE")
                # Get IAM role ARN If stack creation is complete
                if stack_state == "CREATE_COMPLETE":
                    print(f"CREATED stack with name {stack_name}")
                    describe_stack_resp = cloud_formation_client.describe_stacks(StackName=stack_name)
                    stack_outputs = describe_stack_resp['Stacks'][0]['Outputs']
                    outputs = dict()
                    for output in stack_outputs:
                        key = output.get('OutputKey')
                        value = output.get('OutputValue')
                        outputs[key] = value
                    iam_role_arn = outputs.get('PrismaCloudRoleARN')
                    if iam_role_arn is None:
                        sys.exit(f"PrismaCloudRoleARN is not present in outputs for the stack: {stack_name}")
                # Login again, In case if the token is expired
                response = requests.request("POST", login_url, headers=login_headers, data=login_payload, verify=False)
                YOUR_TOKEN = response.json()['token']
                # 3. Onboard your AWS account to Prisma Cloud
                save_account_url = f"{base_url}/cas/v1/aws_account"
                save_account_payload = json.dumps({
                  "accountId": str({accountId}),
                  "accountType": "account",
                  "enabled": True,
                  "name": "AI_based_onboarding-" + str({accountId}),
                  "roleArn": iam_role_arn,
                  "features": [
                    {
                      "name": "Agentless Scanning",
                      "state": "enabled"
                    },
                    {
                      "name": "Auto Protect",
                      "state": "disabled"
                    },
                    {
                      "name": "Remediation",
                      "state": "disabled"
                    },
                    {
                      "name": "Serverless Function Scanning",
                      "state": "enabled"
                    }
                  ]
                })
                save_account_headers = {
                  'Content-Type': 'application/json',
                  'Accept': 'application/json',
                  'x-redlock-auth': YOUR_TOKEN
                }
                response = requests.request("POST", save_account_url, headers=save_account_headers, data=save_account_payload,
                                            verify=False)
                if response.status_code == 200:
                    print("Successfully onboarded account")
                else:
                    print(f"failed to Onboard account. status_code: {response.status_code}")
                    print(f"failed to Onboard account. response: {response.text}")
                    print(f"failed to Onboard account. status: {response.headers.get('x-redlock-status')}")
            """
            code = code.replace("{accountId}", "\"" + account_id + "\"")
            response = "Copy the code below into a python file to automatically onboard your cloud account." \
                       " The script needs access to your AWS env variables and must have the required permissions " \
                       "to perform the automation. \n" + code
            return response
        case _:
            return 'Code gen not supported for cloud type %s. Please go to the manual flow' % cloud_type
