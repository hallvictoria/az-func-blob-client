import json
import os

from typing import Any, Optional

from azfuncbindingbase import Datum, InConverter, OutConverter, SdkType
from .blobClient import BlobClient

class BlobClientConverter(InConverter,
                          OutConverter,
                          binding='blob',
                          trigger='blobTrigger',):
    
    @classmethod
    def check_input_type_annotation(cls, pytype: type) -> bool:
        return issubclass(pytype, (BlobClient, bytes, str))

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
