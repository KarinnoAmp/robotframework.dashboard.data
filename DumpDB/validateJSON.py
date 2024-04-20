import jsonschema
import json
import os
import unittest


class validateJSONSchema:
    def __init__(self) -> None:
        with open(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "Config", "schemaConfig.json")
        ) as json_schema_file:
            self.json_schema = json.load(json_schema_file)

    def validateJSON(self, json_object: dict):
        try:
            jsonschema.validate(json_object, self.json_schema)
        except:
            raise(ValueError("JSON data is invalid."))

class unittest_validateJSONSchema(unittest.TestCase):
    def setUp(self) -> None:
        self.validateJSONSchema = validateJSONSchema()

    def test_validateJSON_success(self):
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "unittestData", "sample_data.json")) as json_file:
            json_data = json.load(json_file)
        self.assertNoLogs(self.validateJSONSchema.validateJSON(json_data))

    def test_validateJSON_fail(self):
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "unittestData", "wrongSchema_sample_data.json")) as json_file:
            json_data = json.load(json_file)
        with self.assertRaises(ValueError, msg="JSON data is invalid."):
            self.validateJSONSchema.validateJSON(json_data)

if __name__ == '__main__':
    unittest.main()