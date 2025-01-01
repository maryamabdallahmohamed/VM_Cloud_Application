import unittest
from unittest.mock import patch, MagicMock
import json
import requests
import os

from app import DesktopApplication


class TestDockerHubSearch(unittest.TestCase):
    def setUp(self):
        self.app = DesktopApplication()

        # Hide the main window to avoid popping up a GUI during tests
        self.app.withdraw()

    def tearDown(self):
        # Destroy the application after each test
        self.app.destroy()

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


class TestVMCreation(unittest.TestCase):
    def setUp(self):
        """
        Setup runs before each test. We instantiate the application
        and hide the UI to avoid popping up windows.
        """
        self.app = DesktopApplication()
        
        # Hide the main window to avoid actually showing a GUI during tests
        self.app.withdraw()

        self.app.cpu_var.set("1")
        self.app.memory_var.set("1024")
        fake_disk_path = "/fake/path.qcow2"
        self.app.disk_var.set(fake_disk_path)

    def tearDown(self):
        self.app.destroy()

    # Mock the 'subprocess.Popen' so we dont actually start qemu
    @patch('subprocess.Popen')
    def test_create_vm_successful_launch(self, mock_popen):
        """
        Test that create_vm() launches QEMU with correct arguments
        when provided valid inputs.
        """
        
        # We also ensure the file 'exists' by mocking os.path.exists to return True.
        with patch('os.path.exists', return_value=True):
            # We expect an info msg that, so lets patch it to then trace it
            with patch('tkinter.messagebox.showinfo') as mock_msgbox:
                with patch('tkinter.messagebox.showerror') as errorbox:
                    self.app.create_vm()

        # Assert
        # Ensure subprocess.Popen was called exactly once
        mock_popen.assert_called_once()

        # Retrieve the args that Popen was called with
        call_args = mock_popen.call_args[0][0]

        # We expect certain flags to be in the QEMU command
        self.assertIn("qemu-system-x86_64", call_args)
        self.assertIn("-smp", call_args)
        self.assertIn("1", call_args)         # CPU count
        self.assertIn("-m", call_args)
        self.assertIn("1024", call_args)      # Memory
        self.assertTrue(any("file=/fake/path.qcow2" in arg for arg in call_args))

        # Assert that an info pop up appeared
        mock_msgbox.assert_called_once()
        args, _ = mock_msgbox.call_args
        self.assertIn("Virtual machine launched!", args[1])


    @patch('subprocess.Popen')
    def test_create_vm_invalid_disk(self, mock_popen):
        """
        Test create_vm() behavior when disk path does not exist.
        It should NOT call subprocess.Popen and should show an error.
        """

        # Mock os.path.exists to return False, simulating a non-existent file
        with patch('os.path.exists', return_value=False):
            # We expect an error popup, so let's also patch messagebox.showerror
            with patch('tkinter.messagebox.showerror') as mock_msgbox:
                self.app.create_vm()
        
        # Assert
        mock_popen.assert_not_called()
        mock_msgbox.assert_called_once()
        args, _ = mock_msgbox.call_args
        self.assertIn("Disk image file does not exist!", args[1])

    @patch('subprocess.Popen')
    def test_create_vm_invalid_cpu_memory(self, mock_popen):
        """
        Test create_vm() with invalid CPU or memory values (non-numeric).
        Should show an error and not call Popen.
        """
        self.app.cpu_var.set("invalid_cpu")
        self.app.memory_var.set("invalid_memory")
        self.app.disk_var.set("/fake/path.qcow2")

        # We also simulate that the disk file does exist
        with patch('os.path.exists', return_value=True):
            with patch('tkinter.messagebox.showerror') as mock_msgbox:
                self.app.create_vm()

        # Assert that an error pops up
        mock_popen.assert_not_called()
        mock_msgbox.assert_called_once()
        args, _ = mock_msgbox.call_args
        self.assertIn("Please enter valid numeric values", args[1])

if __name__ == "__main__":
    unittest.main()
