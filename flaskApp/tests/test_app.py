import unittest
from flask import Flask
import os

import importlib.util

spec = importlib.util.spec_from_file_location("flask_app", os.path.join(os.path.dirname(__file__), "..", "app.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

app = module.app
predict_drug_response = module.predict_drug_response
predictions_df = module.predictions_df


class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    def test_predict_sensitive(self):
        result = predict_drug_response("PC3_PROSTATE", "Erlotinib", module.default_threshold)
        self.assertEqual(result, "Sensitive")

    def test_predict_resistant(self):
        result = predict_drug_response("MEG01_HAEMATOPOIETIC_AND_LYMPHOID_TISSUE", "AZD0530", module.default_threshold)
        self.assertEqual(result, "Resistant")

    def test_download_sensitive_csv(self):
        resp = self.client.get("/download_sensitive_csv/PC3_PROSTATE/Erlotinib")
        self.assertEqual(resp.status_code, 200)


if __name__ == "__main__":
    unittest.main()
