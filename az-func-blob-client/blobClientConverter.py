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

        # if not trigger_metadata:
        #     # return blobClient INSTEAD
        #     return InputStream(data=data)
        # else:
        #     properties = cls._decode_trigger_metadata_field(
        #         trigger_metadata, 'Properties', python_type=dict)
        #     if properties:
        #         blob_properties = properties
        #         length = properties.get('Length')
        #         length = int(length) if length else None
        #     else:
        #         blob_properties = None
        #         length = None

        #     metadata = None
        #     try:
        #         metadata = cls._decode_trigger_metadata_field(trigger_metadata,
        #                                                       'Metadata',
        #                                                       python_type=dict)
        #     except (KeyError, ValueError):
        #         # avoiding any exceptions when fetching Metadata as the
        #         # metadata type is unclear.
        #         pass

        #     # return blobClient INSTEAD
        #     # SWITCH STATEMENT HERE ON SPECIFIC PY TYPE
        #     return InputStream(
        #         data=data,
        #         name=cls._decode_trigger_metadata_field(
        #             trigger_metadata, 'BlobTrigger', python_type=str),
        #         length=length,
        #         uri=cls._decode_trigger_metadata_field(
        #             trigger_metadata, 'Uri', python_type=str),
        #         blob_properties=blob_properties,
        #         metadata=metadata
        #     )
