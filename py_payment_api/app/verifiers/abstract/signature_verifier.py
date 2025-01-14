from abc import ABC, abstractmethod
from typing import final
import os

class SignatureVerifier(ABC):
    _secret : str

    def __init__(self, secret_key : str) -> None:
        self.__get_secret_from_env(secret_key)

    @final
    def verify_header_signature(self, data: str, header) -> None:
        if not self.verify_signature(data,self.get_signature_from_header(header)):
            raise ValueError('Bad signature')

    @abstractmethod
    def verify_signature(self, data: str, signature: str) -> bool:
        pass

    @abstractmethod
    def get_signature_from_header(self,header):
        pass

    def __get_secret_from_env(self,key : str):
        secret : str | None = os.getenv('GOOGLE_PUBLIC_KEY')
        if not secret:
            raise ValueError("Google public key not set in environment variables.")
        else:
            self._secret = secret