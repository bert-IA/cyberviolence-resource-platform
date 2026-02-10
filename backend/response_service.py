"""
Service centralisé pour les réponses standardisées et la gestion des erreurs
Élimine la redondance des try/except partout dans le code
"""
from fastapi.responses import JSONResponse
import logging
from typing import Any, Dict, Optional, Callable
import functools
from datetime import datetime

logger = logging.getLogger(__name__)


class ResponseService:
    """Service pour formater les réponses API de manière standardisée"""
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "OK",
        additional: Dict = None,
        status_code: int = 200
    ) -> Dict:
        """Retourne une réponse de succès standardisée"""
        response = {
            "success": True,
            "message": message,
            "data": data
        }
        if additional:
            response.update(additional)
        return response
    
    @staticmethod
    def error(
        message: str,
        error_type: str = "ERROR",
        status_code: int = 500,
        additional: Dict = None
    ) -> tuple:
        """Retourne une réponse d'erreur standardisée"""
        response = {
            "success": False,
            "message": message,
            "error_type": error_type
        }
        if additional:
            response.update(additional)
        
        return JSONResponse(content=response, status_code=status_code)
    
    @staticmethod
    def validation_error(
        message: str,
        field: str = None,
        additional: Dict = None
    ):
        """Erreur de validation"""
        data = {"field": field} if field else {}
        if additional:
            data.update(additional)
        
        return ResponseService.error(
            message=message,
            error_type="VALIDATION_ERROR",
            status_code=400,
            additional={"data": data}
        )
    
    @staticmethod
    def not_found(resource: str = "Resource"):
        """Ressource non trouvée"""
        return ResponseService.error(
            message=f"{resource} not found",
            error_type="NOT_FOUND",
            status_code=404
        )
    
    @staticmethod
    def unauthorized():
        """Non autorisé"""
        return ResponseService.error(
            message="Unauthorized access",
            error_type="UNAUTHORIZED",
            status_code=401
        )
    
    @staticmethod
    def server_error(error: Exception = None):
        """Erreur serveur générique"""
        message = f"Server error: {str(error)}" if error else "Internal server error"
        return ResponseService.error(
            message=message,
            error_type="SERVER_ERROR",
            status_code=500
        )


class ErrorHandler:
    """Décorateur pour gérer automatiquement les erreurs dans les endpoints"""
    
    @staticmethod
    def async_handler(default_status: int = 500):
        """Décorateur pour les endpoints async"""
        def decorator(func: Callable):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except ValueError as e:
                    logger.warning(f"Validation error in {func.__name__}: {e}")
                    return ResponseService.error(
                        message=str(e),
                        error_type="VALIDATION_ERROR",
                        status_code=400
                    )
                except FileNotFoundError as e:
                    logger.warning(f"Resource not found in {func.__name__}: {e}")
                    return ResponseService.not_found()
                except PermissionError as e:
                    logger.warning(f"Permission denied in {func.__name__}: {e}")
                    return ResponseService.unauthorized()
                except Exception as e:
                    logger.error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
                    return ResponseService.server_error(e)
            
            return wrapper
        return decorator
    
    @staticmethod
    def sync_handler(default_status: int = 500):
        """Décorateur pour les endpoints sync"""
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except ValueError as e:
                    logger.warning(f"Validation error in {func.__name__}: {e}")
                    return ResponseService.error(
                        message=str(e),
                        error_type="VALIDATION_ERROR",
                        status_code=400
                    )
                except FileNotFoundError as e:
                    logger.warning(f"Resource not found in {func.__name__}: {e}")
                    return ResponseService.not_found()
                except PermissionError as e:
                    logger.warning(f"Permission denied in {func.__name__}: {e}")
                    return ResponseService.unauthorized()
                except Exception as e:
                    logger.error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
                    return ResponseService.server_error(e)
            
            return wrapper
        return decorator


class OperationLogger:
    """Logger standardisé pour les opérations critiques"""
    
    @staticmethod
    def log_operation(
        operation: str,
        status: str = "started",
        data: Dict = None,
        level: str = "INFO"
    ):
        """Log une opération avec contexte"""
        message = f"[{operation}] {status}"
        if data:
            message += f" | {data}"
        
        getattr(logger, level.lower())(message)
    
    @staticmethod
    def log_success(
        operation: str,
        message: str = "Success",
        data: Dict = None
    ):
        """Log une opération réussie"""
        OperationLogger.log_operation(
            operation,
            f"✓ {message}",
            data,
            "INFO"
        )
    
    @staticmethod
    def log_error(
        operation: str,
        error: Exception,
        data: Dict = None
    ):
        """Log une erreur d'opération"""
        OperationLogger.log_operation(
            operation,
            f"✗ Error: {str(error)}",
            data,
            "ERROR"
        )


# Exemple d'utilisation dans un endpoint:
# @app.get("/some/endpoint")
# @ErrorHandler.async_handler()
# async def some_endpoint():
#     OperationLogger.log_operation("some_endpoint", "started")
#     try:
#         result = await some_operation()
#         OperationLogger.log_success("some_endpoint", "Operation completed", {"id": result.id})
#         return ResponseService.success(result)
#     except Exception as e:
#         OperationLogger.log_error("some_endpoint", e)
#         raise
