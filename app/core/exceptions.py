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
        
        
class UserAlreadyExistsError(Exception):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"User with email '{email}' already exists.")
        
        
        
class UserNotFoundError(Exception):
    def __init__(self, user_cred: int | str | None):
        self.user_cred = user_cred
        super().__init__(f"User with credentials {user_cred} was not found.")
        
