import json
import os

from typing import Any, Optional

from az.func.binding.base import Datum, InConverter, OutConverter, SdkType
from .blobClient import BlobClient

class BlobClientConverter(InConverter,
                          OutConverter,
                          binding='blob',
                          trigger='blobTrigger',):
    
    @classmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, (SdkType, bytes, str))

    @classmethod
    def check_output_type_annotation(cls, pytype: type) -> bool:
        return (
            issubclass(pytype, (str, bytes, bytearray, SdkType))
            or callable(getattr(pytype, 'read', None))
        )

    @classmethod
    def encode(cls, obj: Any, *,
               expected_type: Optional[type]) -> Datum:
        if callable(getattr(obj, 'read', None)):
            # file-like object
            obj = obj.read()

        if isinstance(obj, str):
            return Datum(type='string', value=obj)

        elif isinstance(obj, (bytes, bytearray)):
            return Datum(type='bytes', value=bytes(obj))

        else:
            raise NotImplementedError

    @classmethod
    # NEED TO ADD PYTYPE AS ADDITIONAL PARAMETER
    # do I need to parse the trigger_metadata?
    def decode(cls, data: Datum, *, trigger_metadata) -> Any:
        if data is None or data.type is None:
            return None

        data_type = data.type

        if data_type == 'model_binding_data':
            data = data.value
        else:
            raise ValueError(
                f'unexpected type of data received for the "blob" binding '
                f': {data_type!r}'
            )

        # SWITCH STATEMENT HERE ON SPECIFIC PY TYPE

        return BlobClient(data=data).get_sdk_type()
