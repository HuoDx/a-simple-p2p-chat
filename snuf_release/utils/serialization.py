"""
This module takes care of serializing/deserializing data.
"""
import json



# why? 'cuz I don't want the `encoding='UTF-8'` appearing everywhere.
def json_string_to_bytes(json_string: str) -> bytes:
    return bytes(json_string, encoding='UTF-8')

def serialize(dict_object: dict) -> bytes:
    return json_string_to_bytes(json.dumps(dict_object))

def deserialize(bytes_object: bytes) -> dict:
    return json.loads(bytes_object.decode('UTF-8'))

