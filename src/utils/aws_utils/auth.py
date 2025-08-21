import boto3

class LocalAuth():

    def __init__(self, key_path, manual_auth=False):
        self.key_path= key_path
        self.manual_auth = manual_auth

    def get_keys(self):
        """
        Fetches the AWS Keys from a shared CSV file.
        """
        try:
            with open(self.key_path, "r") as f:
                keys = f.read().strip()
                parts = [part.strip() for part in keys.split(",")]
                self.access_key = parts[1].split("\n")[1].strip()
                self.secret_key = parts[2].strip()        
        except Exception as e:
            return f"ERROR: {str(e)}"


    def get_client(self, service: str):
        """
        Creates an AWS client using manual access and secret keys.
        """
        if not self.manual_auth:
            self.client = boto3.client(service)
        
        else:
            self.get_keys()
            self.client = boto3.client(
                service,
                aws_access_key_id = self.access_key,
                aws_secret_access_key = self.secret_key,
            )

        return self.client

    def get_resource(self, service: str):
        """
        Creates an AWS resource using manual access and secret keys.
        """
        if not self.manual_auth:
            self.client = boto3.resource(service)
        
        else:
            self.get_keys()
            self.client = boto3.resource(
                service,
                aws_access_key_id = self.access_key,
                aws_secret_access_key = self.secret_key,
            )
            
        return self.client    
