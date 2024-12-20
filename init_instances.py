import boto3
import logging
import base64
import time 

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def create_instances(instance_count, base_name, image_id, instance_type, key_name, security_group_id, subnet_id, git_repo_url, script_to_run, region):
    ec2_client = boto3.client("ec2", region_name=region)

    logging.info(f"Starting to create {instance_count} instances...")

    for i in range(instance_count):
        instance_name = f"{base_name}_{i + 1}"
        logging.info(f"Creating instance: {instance_name}...")

        # Define user data script for each instance
        user_data_script = f"""#!/bin/bash
        exec > /var/log/user-data.log 2>&1
        set -x

        # Update and install dependencies
        yum update -y
        yum install -y python3 python3-pip git

        # Clone the repository and run the script
        cd /opt
        git clone {git_repo_url}
        cd {git_repo_url.split('/')[-1].replace('.git', '')}
        pip3 install -r requirements.txt
        nohup python3 {script_to_run}.py {i + 1} > /var/log/{script_to_run.replace('.py', '')}_instance_{i + 1}.log 2>&1 &
        """
        
        print(user_data_script)

        # Base64 encode the user data script
        user_data_encoded = base64.b64encode(user_data_script.encode("utf-8")).decode("utf-8")

        try:
            # Create an EC2 instance
            response = ec2_client.run_instances(
                ImageId=image_id,
                InstanceType=instance_type,
                KeyName=key_name,
                MinCount=1,
                MaxCount=1,
                SecurityGroupIds=[security_group_id],
                SubnetId=subnet_id,
                UserData=user_data_encoded,
                TagSpecifications=[
                    {
                        "ResourceType": "instance",
                        "Tags": [
                            {"Key": "Name", "Value": instance_name}
                        ]
                    }
                ]
            )

            # Log instance details
            instance_id = response["Instances"][0]["InstanceId"]
            logging.info(f"Instance launched with ID: {instance_id} and Name: {instance_name}")

            # Add a delay of 1 minute between instance creations
            logging.info(f"Waiting 1 minute before creating the next instance...")
            time.sleep(60)  # Wait for 1 minute

        except Exception as e:
            logging.error(f"Failed to create instance {instance_name}: {str(e)}")

    logging.info(f"All {instance_count} instances have been created successfully.")

if __name__ == "__main__":
    INSTANCE_COUNT = 2  
    BASE_NAME = "worker"
    IMAGE_ID = "ami-0a0e5d9c7acc336f1"
    INSTANCE_TYPE = "t2.micro"
    KEY_NAME = "python-aws-script"
    SECURITY_GROUP_ID = "sg-074e1dbc43c863f73"  # Replace with your Security Group ID
    SUBNET_ID = "subnet-090da7fa9931cdc44"  # Replace with your Subnet ID
    REGION = "us-east-1"  

    GIT_REPO_URL = "https://github.com/devevangel/python_aws_script.git"
    SCRIPT_TO_RUN = "main"

    create_instances(
        instance_count=INSTANCE_COUNT,
        base_name=BASE_NAME,
        image_id=IMAGE_ID,
        instance_type=INSTANCE_TYPE,
        key_name=KEY_NAME,
        security_group_id=SECURITY_GROUP_ID,
        subnet_id=SUBNET_ID,
        git_repo_url=GIT_REPO_URL,
        script_to_run=SCRIPT_TO_RUN,
        region=REGION
    )
