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


class OrderNotFoundError(Exception):
    def __init__(self, order_id: int | str):
        self.order_id = order_id
        super().__init__(f"Order '{order_id}' was not found.")


class InsufficientStockError(Exception):
    def __init__(self, item_name: str, available: int, requested: int):
        self.item_name = item_name
        self.available = available
        self.requested = requested
        super().__init__(
            f"Insufficient stock for '{item_name}': "
            f"available={available}, requested={requested}."
        )


class EmptyCartError(Exception):
    def __init__(self):
        super().__init__("No selected items in cart to checkout.")


class InvalidOrderTypeError(Exception):
    def __init__(self, message: str = "Invalid order type for this operation."):
        super().__init__(message)
