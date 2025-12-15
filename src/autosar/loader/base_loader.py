"""
Base loader abstract class and common utilities.

Provides the foundation for all file loaders in the system.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Generic, TypeVar
from pathlib import Path
import logging

# Type variable for model types
T = TypeVar('T')


class LoaderException(Exception):
    """Base exception for loader errors."""
    pass


class FileNotFoundError(LoaderException):
    """Raised when a file cannot be found."""
    pass


class ParserError(LoaderException):
    """Raised when file parsing fails."""
    pass


class ValidationError(LoaderException):
    """Raised when data validation fails."""
    pass


class ConversionError(LoaderException):
    """Raised when data conversion to model fails."""
    pass


class UnsupportedFormatError(LoaderException):
    """Raised when file format is not supported."""
    pass


class BaseLoader(ABC, Generic[T]):
    """
    Abstract base class for all file loaders.
    
    Implements the template pattern for loading and converting files:
    1. Load file -> raw data
    2. Validate raw data
    3. Convert to model objects
    
    Subclasses must implement:
    - load(): Parse file content
    - validate(): Validate parsed data
    - to_model(): Convert to model objects
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize loader.
        
        Args:
            logger: Optional logger instance. If None, creates default logger.
        """
        self.logger = logger or logging.getLogger(self.__class__.__name__)
    
    def _validate_file_exists(self, file_path: str) -> Path:
        """
        Check if file exists.
        
        Args:
            file_path: Path to file
            
        Returns:
            Path object if file exists
            
        Raises:
            FileNotFoundError: If file does not exist
        """
        path = Path(file_path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if not path.is_file():
            raise FileNotFoundError(f"Path is not a file: {path}")
        return path
    
    def _validate_file_extension(self, file_path: Path, 
                                  extensions: List[str]) -> None:
        """
        Validate file has correct extension.
        
        Args:
            file_path: Path to file
            extensions: List of valid extensions (e.g., ['.dbc', '.DBC'])
            
        Raises:
            UnsupportedFormatError: If extension is not valid
        """
        if file_path.suffix.lower() not in [ext.lower() for ext in extensions]:
            raise UnsupportedFormatError(
                f"Unsupported file extension: {file_path.suffix}. "
                f"Expected one of: {', '.join(extensions)}"
            )
    
    @abstractmethod
    def load(self, file_path: str) -> Dict[str, Any]:
        """
        Load and parse file.
        
        Args:
            file_path: Path to file to load
            
        Returns:
            Dictionary containing parsed data
            
        Raises:
            FileNotFoundError: If file does not exist
            ParserError: If parsing fails
        """
        pass
    
    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> bool:
        """
        Validate parsed data structure.
        
        Args:
            data: Parsed data to validate
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If data is invalid
        """
        pass
    
    @abstractmethod
    def to_model(self, data: Dict[str, Any]) -> T:
        """
        Convert parsed data to model objects.
        
        Args:
            data: Validated parsed data
            
        Returns:
            Model object(s)
            
        Raises:
            ConversionError: If conversion fails
        """
        pass
    
    def load_and_convert(self, file_path: str) -> T:
        """
        Load file and convert to model objects (convenience method).
        
        Combines load(), validate(), and to_model() in one call.
        
        Args:
            file_path: Path to file to load
            
        Returns:
            Model object(s)
            
        Raises:
            LoaderException: If any step fails
        """
        self.logger.info(f"Loading file: {file_path}")
        
        try:
            # Load file
            data = self.load(file_path)
            self.logger.debug(f"Loaded data with {len(data)} top-level keys")
            
            # Validate
            self.validate(data)
            self.logger.debug("Data validation successful")
            
            # Convert to model
            model = self.to_model(data)
            self.logger.info("File loaded and converted successfully")
            
            return model
            
        except LoaderException:
            # Re-raise loader exceptions
            raise
        except Exception as e:
            # Wrap other exceptions
            self.logger.error(f"Unexpected error: {e}", exc_info=True)
            raise LoaderException(f"Failed to load file: {e}") from e


class CachedLoader(BaseLoader[T]):
    """
    Base loader with caching support.
    
    Caches loaded files to avoid re-parsing the same file multiple times.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize cached loader."""
        super().__init__(logger)
        self._cache: Dict[str, T] = {}
    
    def load_and_convert(self, file_path: str, use_cache: bool = True) -> T:
        """
        Load file with optional caching.
        
        Args:
            file_path: Path to file to load
            use_cache: If True, use cached result if available
            
        Returns:
            Model object(s)
        """
        # Resolve path for cache key
        resolved_path = str(Path(file_path).resolve())
        
        # Check cache
        if use_cache and resolved_path in self._cache:
            self.logger.debug(f"Using cached result for: {file_path}")
            return self._cache[resolved_path]
        
        # Load and convert
        result = super().load_and_convert(file_path)
        
        # Store in cache
        if use_cache:
            self._cache[resolved_path] = result
            self.logger.debug(f"Cached result for: {file_path}")
        
        return result
    
    def clear_cache(self) -> None:
        """Clear the cache."""
        self._cache.clear()
        self.logger.debug("Cache cleared")
