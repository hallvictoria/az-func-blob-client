#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
import json
import unittest
from typing import Any, Dict

from azfuncbindingbase import Datum

from azfuncblobclient import ContainerClient
from azfuncblobclient import blobClientConverter


class TestBlob(unittest.TestCase):
    def test_input_type(self):
        check_input_type = blobClientConverter.check_input_type_annotation
        self.assertTrue(check_input_type(ContainerClient))
        self.assertFalse(check_input_type(str))
        self.assertFalse(check_input_type(bytes))
        self.assertFalse(check_input_type(bytearray))

    def test_input_none(self):
        result = blobClientConverter.decode(
            data=None, trigger_metadata=None, pytype=ContainerClient)
        self.assertIsNone(result)

    def test_input_incorrect_type(self):
        datum: Datum = Datum(value=b'string_content', type='bytearray')
        with self.assertRaises(ValueError):
            blobClientConverter.decode(data=datum, trigger_metadata=None, pytype=ContainerClient)

    def test_input_empty(self):
        datum: Datum = Datum(value='{}', type='model_binding_data')
        result: ContainerClient = blobClientConverter.decode(
            data=datum, trigger_metadata=None, pytype=ContainerClient)
        self.assertIsNotNone(result)

        # Verify result metadata
        self.assertIsInstance(result, ContainerClient)
        self.assertIsNone(result._version)
        self.assertIsNone(result._source)
        self.assertIsNone(result._content_type)
        self.assertIsNone(result._connection)
        self.assertIsNone(result._containerName)
        self.assertIsNone(result._blobName)

    def test_input_populated(self):
        sample_mbd = {"version": "1.0",
                      "source": "AzureStorageBlobs",
                      "content_type": "application/json",
                      "content": "{\"Connection\":\"AzureWebJobsStorage\",\"ContainerName\":\"test-blob\",\"BlobName\":\"test.txt\"}"}


        datum: Datum = Datum(value=sample_mbd, type='model_binding_data')
        result: ContainerClient = blobClientConverter.decode(data=datum,
                                                        trigger_metadata=None,
                                                        pytype=ContainerClient)

        # Verify result metadata
        self.assertIsInstance(result, ContainerClient)
        self.assertIsEqual(result._version, "1.0")
        self.assertIsEqual(result._source, "AzureStorageBlobs")
        self.assertIsEqual(result._content_type, "application/json")
        self.assertIsEqual(result._connection, "AzureWebJobsStorage")
        self.assertIsEqual(result._containerName, "test-blob")
        self.assertIsEqual(result._blobName, "test.txt")
