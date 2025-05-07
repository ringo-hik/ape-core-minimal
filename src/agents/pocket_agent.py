"""
Pocket (S3) Agent for APE-Core

This module provides integration with S3-compatible storage services like Pocket.
"""

import os
import json
import boto3
from botocore.exceptions import ClientError
from typing import Dict, List, Any, Optional, BinaryIO, Union
from ..core.agent_interface import ServiceAgent

class PocketAgent(ServiceAgent):
    """Agent for interacting with S3-compatible storage (Pocket)"""
    
    def __init__(self):
        """Initialize the Pocket (S3) agent"""
        self.endpoint_url = os.environ.get("APE_POCKET_ENDPOINT", "https://internal-pocket-instance.com")
        self.access_key = os.environ.get("APE_POCKET_ACCESS_KEY", "dummy-access-key")
        self.secret_key = os.environ.get("APE_POCKET_SECRET_KEY", "dummy-secret-key")
        self.region = os.environ.get("APE_POCKET_REGION", "us-east-1")
        self.default_bucket = os.environ.get("APE_POCKET_DEFAULT_BUCKET", "ape-data")
        
        # Initialize S3 client
        self.s3_client = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region
        )
    
    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a Pocket/S3 related request
        
        Args:
            request: The request to process
            
        Returns:
            Response dictionary
        """
        if not self.validate_request(request):
            return {"success": False, "error": "Invalid request format"}
        
        action = request.get("action", "")
        
        if action == "list_buckets":
            return self.list_buckets()
        elif action == "list_objects":
            return self.list_objects(
                request.get("bucket", self.default_bucket),
                request.get("prefix", ""),
                request.get("max_keys", 1000)
            )
        elif action == "get_object":
            return self.get_object(
                request.get("bucket", self.default_bucket),
                request.get("key", ""),
                request.get("version_id", None)
            )
        elif action == "put_object":
            return self.put_object(
                request.get("bucket", self.default_bucket),
                request.get("key", ""),
                request.get("data", ""),
                request.get("metadata", None)
            )
        elif action == "delete_object":
            return self.delete_object(
                request.get("bucket", self.default_bucket),
                request.get("key", "")
            )
        elif action == "create_bucket":
            return self.create_bucket(
                request.get("bucket", ""),
                request.get("region", self.region)
            )
        else:
            return {"success": False, "error": f"Unsupported action: {action}"}
    
    def get_capabilities(self) -> List[str]:
        """
        Get the capabilities of this agent
        
        Returns:
            List of capability strings
        """
        return [
            "list_buckets",
            "list_objects",
            "get_object",
            "put_object",
            "delete_object",
            "create_bucket"
        ]
    
    def validate_request(self, request: Dict[str, Any]) -> bool:
        """
        Validate if a request can be processed by this agent
        
        Args:
            request: The request to validate
            
        Returns:
            True if the request is valid, False otherwise
        """
        if not isinstance(request, dict):
            return False
        
        if "action" not in request:
            return False
        
        action = request.get("action", "")
        
        if action not in self.get_capabilities():
            return False
        
        # Specific validations
        if action == "put_object" and "key" not in request:
            return False
        
        if action == "get_object" and "key" not in request:
            return False
        
        if action == "delete_object" and "key" not in request:
            return False
        
        if action == "create_bucket" and "bucket" not in request:
            return False
        
        return True
    
    def authenticate(self) -> bool:
        """
        Authenticate with the S3/Pocket service
        
        Returns:
            True if authentication was successful, False otherwise
        """
        try:
            self.s3_client.list_buckets()
            return True
        except Exception:
            return False
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        Get information about the S3/Pocket service
        
        Returns:
            Service information
        """
        try:
            buckets = self.s3_client.list_buckets()
            return {
                "success": True,
                "data": {
                    "endpoint_url": self.endpoint_url,
                    "region": self.region,
                    "bucket_count": len(buckets.get("Buckets", [])),
                    "default_bucket": self.default_bucket
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_resource(self, resource_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a resource in the S3/Pocket service
        
        Args:
            resource_type: Type of resource to create
            data: Resource data
            
        Returns:
            Created resource data
        """
        if resource_type == "bucket":
            return self.create_bucket(
                data.get("name", ""),
                data.get("region", self.region)
            )
        elif resource_type == "object":
            return self.put_object(
                data.get("bucket", self.default_bucket),
                data.get("key", ""),
                data.get("data", ""),
                data.get("metadata", None)
            )
        else:
            return {"success": False, "error": f"Unsupported resource type: {resource_type}"}
    
    def get_resource(self, resource_type: str, resource_id: str) -> Dict[str, Any]:
        """
        Get a resource from the S3/Pocket service
        
        Args:
            resource_type: Type of resource to get
            resource_id: ID of the resource
            
        Returns:
            Resource data
        """
        if resource_type == "object":
            # For objects, resource_id is the key
            return self.get_object(self.default_bucket, resource_id)
        elif resource_type == "bucket":
            # For buckets, we list objects in the bucket
            return self.list_objects(resource_id)
        else:
            return {"success": False, "error": f"Unsupported resource type: {resource_type}"}
    
    def update_resource(self, resource_type: str, resource_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a resource in the S3/Pocket service
        
        Args:
            resource_type: Type of resource to update
            resource_id: ID of the resource
            data: Updated resource data
            
        Returns:
            Updated resource data
        """
        if resource_type == "object":
            # For objects, resource_id is the key
            return self.put_object(
                data.get("bucket", self.default_bucket),
                resource_id,
                data.get("data", ""),
                data.get("metadata", None)
            )
        else:
            return {"success": False, "error": f"Unsupported resource type: {resource_type}"}
    
    def delete_resource(self, resource_type: str, resource_id: str) -> bool:
        """
        Delete a resource in the S3/Pocket service
        
        Args:
            resource_type: Type of resource to delete
            resource_id: ID of the resource
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            if resource_type == "object":
                # For objects, resource_id is the key
                result = self.delete_object(self.default_bucket, resource_id)
                return result.get("success", False)
            elif resource_type == "bucket":
                # For buckets, resource_id is the bucket name
                self.s3_client.delete_bucket(Bucket=resource_id)
                return True
            else:
                return False
        except Exception:
            return False
    
    def list_buckets(self) -> Dict[str, Any]:
        """
        List all S3 buckets
        
        Returns:
            List of buckets
        """
        try:
            response = self.s3_client.list_buckets()
            
            buckets = []
            for bucket in response.get("Buckets", []):
                buckets.append({
                    "name": bucket.get("Name", ""),
                    "creation_date": bucket.get("CreationDate", "").isoformat() if bucket.get("CreationDate") else ""
                })
            
            return {"success": True, "data": buckets}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_objects(self, bucket: str, prefix: str = "", max_keys: int = 1000) -> Dict[str, Any]:
        """
        List objects in a bucket
        
        Args:
            bucket: Name of the bucket
            prefix: Prefix to filter objects
            max_keys: Maximum number of keys to return
            
        Returns:
            List of objects
        """
        try:
            args = {
                "Bucket": bucket,
                "MaxKeys": max_keys
            }
            
            if prefix:
                args["Prefix"] = prefix
            
            response = self.s3_client.list_objects_v2(**args)
            
            objects = []
            for obj in response.get("Contents", []):
                objects.append({
                    "key": obj.get("Key", ""),
                    "size": obj.get("Size", 0),
                    "last_modified": obj.get("LastModified", "").isoformat() if obj.get("LastModified") else "",
                    "etag": obj.get("ETag", "").strip('"'),
                    "storage_class": obj.get("StorageClass", "")
                })
            
            return {
                "success": True,
                "data": {
                    "objects": objects,
                    "is_truncated": response.get("IsTruncated", False),
                    "key_count": response.get("KeyCount", 0),
                    "continuation_token": response.get("NextContinuationToken", "")
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_object(self, bucket: str, key: str, version_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get an object from a bucket
        
        Args:
            bucket: Name of the bucket
            key: Key of the object
            version_id: Optional version ID
            
        Returns:
            Object data
        """
        try:
            args = {
                "Bucket": bucket,
                "Key": key
            }
            
            if version_id:
                args["VersionId"] = version_id
            
            response = self.s3_client.get_object(**args)
            
            # Get content type
            content_type = response.get("ContentType", "application/octet-stream")
            
            # Read the data
            data = response["Body"].read()
            
            # Handle text-based content types
            if content_type.startswith("text/") or content_type in ["application/json", "application/xml"]:
                try:
                    # Try to decode as text
                    data = data.decode("utf-8")
                    
                    # Parse JSON if it's a JSON content type
                    if content_type == "application/json":
                        try:
                            data = json.loads(data)
                        except json.JSONDecodeError:
                            pass
                except UnicodeDecodeError:
                    # If decoding fails, keep as binary
                    pass
            
            return {
                "success": True,
                "data": {
                    "content": data,
                    "content_type": content_type,
                    "content_length": response.get("ContentLength", 0),
                    "last_modified": response.get("LastModified", "").isoformat() if response.get("LastModified") else "",
                    "etag": response.get("ETag", "").strip('"'),
                    "metadata": response.get("Metadata", {})
                }
            }
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "NoSuchKey":
                return {"success": False, "error": f"Object not found: {key}"}
            else:
                return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def put_object(
        self,
        bucket: str,
        key: str,
        data: Union[str, bytes, BinaryIO],
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Put an object in a bucket
        
        Args:
            bucket: Name of the bucket
            key: Key of the object
            data: Object data
            metadata: Optional metadata
            
        Returns:
            Result of the operation
        """
        try:
            args = {
                "Bucket": bucket,
                "Key": key,
                "Body": data
            }
            
            # Add metadata if provided
            if metadata:
                args["Metadata"] = metadata
            
            # Determine content type based on key extension
            if "." in key:
                extension = key.split(".")[-1].lower()
                if extension == "json":
                    args["ContentType"] = "application/json"
                elif extension == "txt":
                    args["ContentType"] = "text/plain"
                elif extension == "html":
                    args["ContentType"] = "text/html"
                elif extension in ["jpg", "jpeg"]:
                    args["ContentType"] = "image/jpeg"
                elif extension == "png":
                    args["ContentType"] = "image/png"
                elif extension == "pdf":
                    args["ContentType"] = "application/pdf"
            
            response = self.s3_client.put_object(**args)
            
            return {
                "success": True,
                "data": {
                    "etag": response.get("ETag", "").strip('"'),
                    "version_id": response.get("VersionId", "")
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_object(self, bucket: str, key: str) -> Dict[str, Any]:
        """
        Delete an object from a bucket
        
        Args:
            bucket: Name of the bucket
            key: Key of the object
            
        Returns:
            Result of the operation
        """
        try:
            response = self.s3_client.delete_object(
                Bucket=bucket,
                Key=key
            )
            
            return {
                "success": True,
                "data": {
                    "version_id": response.get("VersionId", ""),
                    "delete_marker": response.get("DeleteMarker", False)
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_bucket(self, bucket: str, region: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new bucket
        
        Args:
            bucket: Name of the bucket
            region: Region for the bucket
            
        Returns:
            Result of the operation
        """
        try:
            region_to_use = region or self.region
            
            args = {
                "Bucket": bucket
            }
            
            # Add location constraint if not us-east-1
            if region_to_use != "us-east-1":
                args["CreateBucketConfiguration"] = {
                    "LocationConstraint": region_to_use
                }
            
            response = self.s3_client.create_bucket(**args)
            
            return {
                "success": True,
                "data": {
                    "location": response.get("Location", ""),
                    "bucket": bucket,
                    "region": region_to_use
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}