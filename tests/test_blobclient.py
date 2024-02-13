#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import json
import unittest
from typing import Any, Dict, Optional

from azfuncbindingbase import Datum

from azfuncblobclient import BlobClient
from azfuncblobclient import BlobClientConverter

from azure.storage.blob import BlobClient as BlobClientSdk

class MockMBD:
    def __init__(self, version: str, source: str, content_type: str, content: str):
        self.version = version
        self.source = source
        self.content_type = content_type
        self.content = content

class TestBlobClient(unittest.TestCase):
    def test_input_type(self):
        check_input_type = BlobClientConverter.check_input_type_annotation
        self.assertTrue(check_input_type(BlobClient))
        self.assertFalse(check_input_type(str))
        self.assertFalse(check_input_type(bytes))
        self.assertFalse(check_input_type(bytearray))

    def test_input_none(self):
        decode_result = BlobClientConverter.decode(
            data=None, trigger_metadata=None, pytype=BlobClient)
        self.assertIsNone(decode_result)

    def test_input_incorrect_type(self):
        datum: Datum = Datum(value=b'string_content', type='bytearray')
        with self.assertRaises(ValueError):
            BlobClientConverter.decode(data=datum, trigger_metadata=None, pytype=BlobClient)

    def test_input_empty(self):
        datum: Datum = Datum(value={}, type='model_binding_data')
        decode_result: BlobClient = BlobClientConverter.decode(
            data=datum, trigger_metadata=None, pytype=BlobClient)
        self.assertIsNone(decode_result)

    def test_input_populated(self):
        # TODO: pass in variable connection string
        sample_mbd = MockMBD(version="1.0", source="AzureStorageBlobs", content_type="application/json", content="{\"Connection\":\"AzureWebJobsStorage\",\"ContainerName\":\"test-blob\",\"BlobName\":\"test.txt\"}")

        datum: Datum = Datum(value=sample_mbd, type='model_binding_data')
        result: BlobClient = BlobClientConverter.decode(data=datum,
                                                        trigger_metadata=None,
                                                        pytype=BlobClient)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, BlobClientSdk)

        sdk_result = BlobClient(data=datum).get_sdk_type()

        self.assertIsNotNone(sdk_result)
        self.assertIsInstance(sdk_result, BlobClientSdk)

    def test_blobclient_valid_creation(self):
        class MockBindingDirection:
            IN = 0
            OUT = 1
            INOUT = 2

        class MockBinding:
            def __init__(self, name: str,
                         direction: int,
                         data_type=None,
                         type: Optional[str] = None):  # NoQa
                # For natively supported bindings, get_binding_name is always
                # implemented, and for generic bindings, type is a required argument
                # in decorator functions.
                self.type = type
                self.name = name
                self._direction = direction
                self._data_type = data_type
                self._dict = {
                    "direction": self._direction,
                    "dataType": self._data_type,
                    "type": self.type
                }

        class MockParamTypeInfo:
            def __init__(self, binding_name: str, pytype: type):
                self.binding_name = binding_name
                self.pytype = pytype

        class MockFunction:
            def __init__(self, bindings: MockBinding):
                self._bindings = bindings

        # Create test binding
        mock_blob = MockBinding(name="blob",
                                  direction=MockBindingDirection.IN,
                                  data_type=None, type='blob')

        # Create test input_types dict
        mock_input_types = {"blob": MockParamTypeInfo(
            binding_name='blobTrigger', pytype=bytes)}

        # Create test indexed_function
        mock_indexed_functions = MockFunction(bindings=[mock_blob])

        sample_mbd = MockMBD(version="1.0", source="AzureStorageBlobs", content_type="application/json", content="{\"Connection\":\"AzureWebJobsStorage\",\"ContainerName\":\"test-blob\",\"BlobName\":\"test.txt\"}")
        client = BlobClient(data=sample_mbd)

        dict_repr = BlobClientConverter.get_raw_bindings(mock_indexed_functions)

        self.assertEqual(dict_repr,
                         ['{"direction": "IN", '
                          '"dataType": null, "type": "blob", '
                          '"properties": '
                          '{"SupportsDeferredBinding": true}}'])
