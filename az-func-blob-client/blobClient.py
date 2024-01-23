import json
import os

from az.func.binding.base import Datum, SdkType
from azure.storage.blob import BlobClient as BlobClientSdk
from typing import Any, Optional, Union

# DATA IS MODEL_BINDING_DATA

class BlobClient():
    # Change constructor to only take in data -- parse to get connection string, container name, and blob name
    def __init__(self, *, data: Union[bytes, Datum],
                 name: Optional[str] = None,
                 uri: Optional[str] = None,
                 length: Optional[int] = None,
                 blob_properties: Optional[dict] = None,
                 metadata: Optional[dict] = None) -> None:
        # Blob properties
        self._name = name
        self._length = length
        self._uri = uri
        self._blob_properties = blob_properties
        self._metadata = metadata

        # model_binding_data properties
        self._data = data or {}
        self._version = ""
        self._source = ""
        self._content_type = ""
        self._connection = ""
        self._containerName = ""
        self._blobName = ""
        if data is not {}:
            self._version = data.version
            self._source = data.source
            self._content_type = data.content_type
            content_json = json.loads(data.content)
            self._connection = os.getenv(content_json["Connection"])
            self._containerName = content_json["ContainerName"]
            self._blobName = content_json["BlobName"]

    @property
    def name(self) -> Optional[str]:
        return self._name

    @property
    def length(self) -> Optional[int]:
        return self._length

    @property
    def uri(self) -> Optional[str]:
        return self._uri

    @property
    def blob_properties(self):
        return self._blob_properties

    @property
    def metadata(self):
        return self._metadata

    # THIS IS WHERE WE RETURN THE CLIENT
    def get_sdk_type(self):
        return BlobClientSdk.from_connection_string(
            conn_str=self._connection,
            container_name=self._containerName,
            blob_name=self._blobName
        )