import boto3
import io
import os
import pandas as pd

class S3Handler():
    def __init__(self, bucket, client):
        self.client = client
        self.bucket = bucket
    

    def list_s3_objects(self, prefix: str) -> list:
        """
        List objects in S3 bucket with given prefix
        """
        response = self.client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
        return response.get('Contents', [])


    def get_s3_object(self, prefix: str) -> pd.DataFrame:
        """
        Lists a S3 prefix and reads the latest Parquet/CSV 
        object to return a Dataframe
        """
        try:
            response = self.client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
            contents = response.get('Contents', [])
            
            if len(contents) >= 1:
                latest_file = sorted(contents, key=lambda x: x['LastModified'], reverse=True)[0]
                key = latest_file['Key']
                
                # Skip if it's just a directory
                if key.endswith('/'):
                    raise ValueError(f"No files found in directory: {key}")
                    
                obj = self.client.get_object(Bucket=self.bucket, Key=key)
                data = obj['Body'].read()
                
                if key.lower().endswith('.parquet'):
                    return pd.read_parquet(io.BytesIO(data))
                elif key.lower().endswith('.csv'):
                    return pd.read_csv(io.BytesIO(data))
                else:
                    raise ValueError(f"Unsupported file type. File must be .csv or .parquet: {key}")
            else:
                raise ValueError("No objects found in the prefix")
                
        except Exception as e:
            print(f"Error reading from S3: {str(e)}")
            raise


    def bulk_download(self, prefix: str, dest: str, resource: boto3, fmt: str = "csv") -> None:
        """
        Downloads all objects within an S3 folder that
        match the specified format.
        """
        if prefix and not prefix.endswith("/"):
            prefix += "/"

        os.makedirs(dest, exist_ok=True)
        b = resource.Bucket(self.bucket)

        for obj in b.objects.filter(Prefix=prefix):
            if obj.key.lower().endswith(fmt) and not obj.key.endswith("/"):
                local = os.path.join(dest, "EOA_" + os.getlogin() + "_" + os.path.basename(obj.key))
                b.download_file(obj.key, local)
                print(f"Downloaded {local}")


    def save_to_s3(self, df: pd.DataFrame, key: str) -> bool:
        """
        Save DataFrame to S3 as CSV file.
        """
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        bytes_data = buffer.getvalue().encode('utf-8')
        
        response = self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=bytes_data,
            ContentType='text/csv'
        )

        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            print(f"Successfully saved CSV to {key}")
            return True
        else:
            print(f"Upload failed with response: {response}")
            return False


    def move_s3_files(self, old_folder: str, new_folder: str, fmt: str= None) -> dict:
        """
        Moves all files in a folder to a different folder
        """
        objects = self.list_s3_objects(old_folder)
        print(f"Found {len(objects)} offer files in the {old_folder} folder.")

        if fmt is not None:
            objects = [obj for obj in objects if obj['Key'].lower().endswith(fmt)]

        results = {"success": [], "fail": []}
        for obj in objects:
            # Define the keys
            source_key = obj["Key"]
            new_key = source_key.replace(old_folder, new_folder)
            print(f"Moving {source_key} → {new_key}")

            try:
                # Copy files to new folder
                self.client.copy_object(
                    Bucket=self.bucket,
                    CopySource={"Bucket": self.bucket, "Key": source_key},
                    Key=new_key
                )
                

                # Delete all in the current folder
                self.client.delete_object(
                    Bucket=self.bucket,
                    Key=source_key
                )

                results["success"].append(source_key)
            
            except Exception as e:
                results["fail"].append(source_key)
                print(f"Error moving {source_key}: {e}")
        
        print(f"Moved {len(results["success"])} files to {new_folder}")
        if len(results["fail"]) != 0:
            print(f"Following files failed to move:")
            for i in results["fail"]:
                print(i)
                

