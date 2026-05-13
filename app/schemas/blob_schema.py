from pydantic import BaseModel

class BlobUploadRead(BaseModel):
    blob_name: str
    blob_url: str
    