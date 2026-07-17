from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AzureBlobUploadError,
    BlobConfigurationError,
    EmptyCartError,
    InsufficientStockError,
    InvalidFileTypeError,
    InvalidOrderTypeError,
    ItemAlreadyExistsError,
    ItemNotFoundError,
    OrderNotFoundError,
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ItemNotFoundError)
    async def item_not_found_handler(
        request: Request,
        exc: ItemNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "detail": str(exc),
                "error_code": "ITEM_NOT_FOUND",
            },
        )

    @app.exception_handler(ItemAlreadyExistsError)
    async def item_already_exists_handler(
        request: Request,
        exc: ItemAlreadyExistsError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "detail": str(exc),
                "error_code": "ITEM_ALREADY_EXISTS",
            },
        )

    @app.exception_handler(InvalidFileTypeError)
    async def invalid_file_type_handler(
        request: Request,
        exc: InvalidFileTypeError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": str(exc),
                "error_code": "INVALID_FILE_TYPE",
            },
        )

    @app.exception_handler(AzureBlobUploadError)
    async def azure_blob_upload_handler(
        request: Request,
        exc: AzureBlobUploadError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={
                "detail": str(exc),
                "error_code": "AZURE_BLOB_UPLOAD_FAILED",
            },
        )

    @app.exception_handler(BlobConfigurationError)
    async def blob_configuration_handler(
        request: Request,
        exc: BlobConfigurationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": str(exc),
                "error_code": "BLOB_CONFIGURATION_ERROR",
            },
        )

    @app.exception_handler(OrderNotFoundError)
    async def order_not_found_handler(
        request: Request,
        exc: OrderNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "detail": str(exc),
                "error_code": "ORDER_NOT_FOUND",
            },
        )

    @app.exception_handler(InsufficientStockError)
    async def insufficient_stock_handler(
        request: Request,
        exc: InsufficientStockError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": str(exc),
                "error_code": "INSUFFICIENT_STOCK",
            },
        )

    @app.exception_handler(EmptyCartError)
    async def empty_cart_handler(
        request: Request,
        exc: EmptyCartError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": str(exc),
                "error_code": "EMPTY_CART",
            },
        )

    @app.exception_handler(InvalidOrderTypeError)
    async def invalid_order_type_handler(
        request: Request,
        exc: InvalidOrderTypeError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": str(exc),
                "error_code": "INVALID_ORDER_TYPE",
            },
        )