from abc import ABC, abstractmethod
from typing import Any, Dict, final
import os

class SignatureVerifier(ABC):
    _secret : str

    def __init__(self, secret_key : str) -> None:
        self.__get_secret_from_env(secret_key)

    @final
    def verify_header_signature(self, data: Dict[str, Any], header : Dict[str, Any]) -> bool:
        if not self.verify_signature(data,self.get_signature_from_header(header)):
            raise ValueError('Bad signature')
        return True

    @abstractmethod
    def verify_signature(self, data: Dict[str, Any], signature: str) -> bool:
        pass

    @abstractmethod
    def get_signature_from_header(self,header : Dict[str, Any]) -> str:
        pass

    def __get_secret_from_env(self,key : str) -> str:
        secret : str | None = os.getenv(key)
        if not secret:
            raise ValueError(f"{key} not set in environment variables.")
        else:
            self._secret = secret
            return self._secret