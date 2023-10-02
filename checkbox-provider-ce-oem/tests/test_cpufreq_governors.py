#!/usr/bin/python3

import unittest
import subprocess
from unittest import mock
"""
We probbley could remove append path while mirge back to ppc.
Since checkbox has __init__.py for unit tests.
ref:
https://github.com/canonical/checkbox/blob/main/checkbox-support/checkbox_support/tests/__init__.py
"""
import sys
import os
# Add the path to the 'bin' directory for the import to work
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'bin'))
from cpufreq_governors import probe_governor_module, CPUScalingInfo


class TestProbeGovernorModule(unittest.TestCase):
    def setUp(self):
        self.expected_governor = ["conservative", "powersave", "ondemand",
                                  "userspace", "performance", "schedutil"]

    def test_governor_module_supported(self):
        # Simulate a scenario where all expected governors are supported
        governor = ["conservative", "powersave", "ondemand",
                    "userspace", "performance", "schedutil"]
        # Simulate a successful modprobe
        status = probe_governor_module(governor, self.expected_governor)
        self.assertEqual(status, 0)

    @mock.patch('subprocess.run')
    def test_governor_module_unsupported_and_probe_success(
            self,
            mock_subprocess_run
            ):
        # Simulate a scenario where some governors are not supported.
        # And probe module success.
        # Create a mock subprocess.CompletedProcess object with a
        # return code of 0
        governor = ["powersave", "ondemand",
                    "userspace", "performance", "schedutil"]
        mock_subprocess_run.returncode = 0
        result = probe_governor_module(governor, self.expected_governor)

        self.assertEqual(result, 0)

    @mock.patch('subprocess.run')
    def test_governor_module_unsupported_and_probe_fail(
            self,
            mock_subprocess_run
            ):
        # Simulate a scenario where some governors are not supported.
        # And probe module fail.
        # Create a mock subprocess.CompletedProcess object with a
        # return code of 1
        governor = ["powersave", "ondemand",
                    "userspace", "performance", "schedutil"]
        cmd = ["modprobe", "cpufreq_powersave"]
        error_message = "Not able to probe cpufreq_conservative!"
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=cmd,
            stderr=error_message
        )
        result = probe_governor_module(governor, self.expected_governor)

        self.assertEqual(result, 1)


class TestCPUScalingInfo(unittest.TestCase):
    def setUp(self):
        self.cpu_scaling_info = CPUScalingInfo()

    @mock.patch('os.listdir')
    def test_get_cpu_policies_success(self, mock_listdir):
        # Mock the listdir function to return a list of CPU policies
        mock_listdir.return_value = ["policy0", "policy1", "policy2"]
        # Call the get_cpu_policies function
        policies = self.cpu_scaling_info.get_cpu_policies()

        # Assert that the function returns the expected list of policies
        self.assertEqual(policies, [0, 1, 2])

    @mock.patch('os.listdir')
    def test_get_cpu_policies_failure(self, mock_listdir):
        # Mock the listdir function to raise an OSError
        mock_listdir.side_effect = OSError("OSError")
        result = self.cpu_scaling_info.get_cpu_policies()
        self.assertEqual(result, [])

    @mock.patch('os.listdir')
    def test_get_cpu_policies_failure_empty(self, mock_listdir):
        # Mock the listdir function to return an empty list
        mock_listdir.return_value = []
        result = self.cpu_scaling_info.get_cpu_policies()
        self.assertEqual(result, [])

    @mock.patch('builtins.open', mock.mock_open(read_data='Driver'))
    def test_get_scaling_driver_success(self):
        # Mock the open function to return a scaling driver
        result = self.cpu_scaling_info.get_scaling_driver()
        self.assertEqual(result, "Driver")

    @mock.patch('builtins.open', side_effect=OSError)
    def test_get_scaling_driver_oserror(self, mock_open):
        # Mock the open function to raise an OSError
        result = self.cpu_scaling_info.get_scaling_driver()
        self.assertEqual(result, "")

    @mock.patch('builtins.open', mock.mock_open(read_data='Attribute_Value'))
    def test_get_attribute_success(self):
        # Mock the open function to return a attribute value
        result = self.cpu_scaling_info.get_attribute("Attribute")
        self.assertEqual(result, "Attribute_Value")

    @mock.patch('builtins.open', side_effect=OSError)
    def test_get_attribute_oserror(self, mock_open):
        # Mock the open function to raise an OSError
        result = self.cpu_scaling_info.get_attribute("Attribute")
        self.assertEqual(result, "")

    @mock.patch('builtins.open', new_callable=mock.mock_open, create=True)
    def test_set_attribute_success(self, mock_open):
        mock_file = mock_open.return_value
        result = self.cpu_scaling_info.set_attribute(
            'attribute_name',
            'new_value')
        mock_file.write.assert_called_once_with('new_value')
        self.assertTrue(result)

    @mock.patch('builtins.open', side_effect=PermissionError)
    def test_set_attribute_permissionerror(self, mock_open):
        # Mock the open function to raise an OSError
        result = self.cpu_scaling_info.set_attribute(
            'attribute_name',
            'new_value')
        self.assertFalse(result)

    @mock.patch('builtins.open', side_effect=OSError)
    def test_set_attribute_oserror(self, mock_open):
        # Mock the open function to raise an OSError
        result = self.cpu_scaling_info.set_attribute(
            'attribute_name',
            'new_value')
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
