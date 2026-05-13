class ItemAlreadyExistsError(Exception):
    def __init__(self, item_name: str):
        self.item_name = item_name
        super().__init__(f"Item with name '{item_name}' already exists.")


class ItemNotFoundError(Exception):
    def __init__(self, item_id: int):
        self.item_id = item_id
        super().__init__(f"Item with id {item_id} was not found.")


class InvalidFileTypeError(Exception):
    def __init__(self, message: str = "Invalid file type."):
        super().__init__(message)


class AzureBlobUploadError(Exception):
    def __init__(self, message: str = "Failed to upload file to Azure Blob Storage."):
        super().__init__(message)


class BlobConfigurationError(Exception):
    def __init__(self, message: str = "Azure Blob Storage configuration error."):
        super().__init__(message)
        
        
class CustomerAlreadyExistsError(Exception):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Customer with email '{email}' already exists.")
        
        
        
class CustomerNotFoundError(Exception):
    def __init__(self, customer_id: int):
        self.customer_id = customer_id
        super().__init__(f"Customer with id {customer_id} was not found.")
        
        
