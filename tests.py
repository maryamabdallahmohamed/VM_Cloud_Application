import unittest
from unittest.mock import patch, MagicMock
import json
import requests

from app import DesktopApplication


class TestDockerHubSearch(unittest.TestCase):
    def setUp(self):
        self.app = DesktopApplication()

        # Hide the main window to avoid popping up a GUI during tests
        self.app.withdraw()

    @patch("requests.get")
    def test_search_docker_hub(self, mock_requests_get):
        """
        Test that searching for 'alpine' yields the expected number of lines in docker_hub_listbox.
        """
        
        # Mock data mimicking Docker Hub API JSON response
        mock_data = {
            "results": [
                {"name": "N/A", "repo_name": "alpine", "star_count": 11147},
                {"name": "N/A", "repo_name": "alpine/git", "star_count": 238},
                {"name": "N/A", "repo_name": "alpine/curl", "star_count": 6},
            ]
        }

        mock_requests_get.return_value = MagicMock(status_code=200, json=lambda: mock_data)
        
        # Click on display_docker_hub_section button to go into the test area
        self.app.display_docker_hub_section()

        # Call the method that performs the Docker Hub search
        self.app.search_docker_hub("alpine")

        # Grab all the text currently in the Textbox
        content = self.app.docker_hub_listbox.get("1.0", "end-1c").strip()
        lines = content.split("\n")

        # We expect 3 lines (since mock_data has 3 results)
        expected_line_count = 3
        self.assertEqual(
            len(lines), 
            expected_line_count,
            f"Expected {expected_line_count} lines, but got {len(lines)}. results of the get:\n{content}"
        )

    @patch("requests.get")
    def test_search_docker_hub_empty_query(self, mock_requests_get):
        """
        Tests that searching with an empty string returns nothing 
        """

        # Mock data mimicking Docker Hub API JSON response
        mock_data = {
            "results": []
        }

        mock_requests_get.return_value = MagicMock(status_code=200, json=lambda: mock_data)

        # Click on display_docker_hub_section button to go into the test area
        self.app.display_docker_hub_section()

        # Call the method that performs the Docker Hub search and search with an empty sstring
        self.app.search_docker_hub("")

        content = self.app.docker_hub_listbox.get("1.0", "end-1c").strip()

        self.assertIn("No results found", content, f"Expected 'No results found' message, got:\n{content}")

    def tearDown(self):
        # Destroy the application after each test
        self.app.destroy()


    @patch("requests.get")
    @patch("tkinter.messagebox.showerror")
    def test_search_docker_hub_network_error(self, mock_showerror, mock_requests_get):
        """
        Simulate a network error when searching Docker Hub
        and verify that a messagebox error is shown.
        """

        mock_requests_get.side_effect = requests.exceptions.ConnectionError("Simulated network failure")

        # Click on display_docker_hub_section button to go into the test area
        self.app.display_docker_hub_section()

        # Call the method that performs the Docker Hub search
        self.app.search_docker_hub("alpine")

        # Check that the app raised the error message in the messagebox
        mock_showerror.assert_called_with(
            "Error",
            "Failed to search Docker Hub: Simulated network failure"
        )

if __name__ == "__main__":
    unittest.main()
