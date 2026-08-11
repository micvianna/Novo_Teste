import os
import unittest
from unittest.mock import patch

import app


class ConfigurationTests(unittest.TestCase):
    def test_missing_configuration_fails_before_request(self):
        with self.assertRaises(app.ConfigurationError):
            app.read_configuration({})

    def test_configuration_comes_from_environment(self):
        values = {
            "CREWAI_KICKOFF_URL": "https://example.invalid/base/",
            "CREWAI_BEARER_TOKEN": "test-only-value",
        }

        base_url, token = app.read_configuration(values)

        self.assertEqual(base_url, "https://example.invalid/base")
        self.assertEqual(token, "test-only-value")

    def test_main_does_not_request_when_configuration_is_missing(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(
            app.st, "title"
        ), patch.object(app.st, "warning"), patch.object(
            app.requests, "request"
        ) as request:
            app.main()

        request.assert_not_called()


if __name__ == "__main__":
    unittest.main()
