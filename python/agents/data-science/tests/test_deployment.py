# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Test cases for the deployment script environment variable filtering."""

import os
import sys
import unittest
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from deployment.deploy import collect_environment_variables


class TestDeploymentEnvironmentVariables(unittest.TestCase):
    """Test cases for deployment environment variable filtering functionality."""

    def test_collect_environment_variables_with_valid_values(self):
        """Test collecting environment variables with valid values."""
        with patch.dict(os.environ, {
            'TEST_VAR1': 'value1',
            'TEST_VAR2': 'value2',
            'TEST_VAR3': 'value3'
        }, clear=False):
            keys = ['TEST_VAR1', 'TEST_VAR2', 'TEST_VAR3']
            result = collect_environment_variables(keys)
            
            expected = {
                'TEST_VAR1': 'value1',
                'TEST_VAR2': 'value2',
                'TEST_VAR3': 'value3'
            }
            self.assertEqual(result, expected)

    def test_collect_environment_variables_filters_none_values(self):
        """Test that None values are filtered out."""
        with patch.dict(os.environ, {
            'TEST_VAR1': 'value1',
            'TEST_VAR2': 'value2'
        }, clear=False):
            # TEST_VAR3 is not in environment, so os.getenv will return None
            keys = ['TEST_VAR1', 'TEST_VAR2', 'TEST_VAR3']
            result = collect_environment_variables(keys)
            
            expected = {
                'TEST_VAR1': 'value1',
                'TEST_VAR2': 'value2'
            }
            self.assertEqual(result, expected)

    def test_collect_environment_variables_filters_empty_strings(self):
        """Test that empty strings are filtered out."""
        with patch.dict(os.environ, {
            'TEST_VAR1': 'value1',
            'TEST_VAR2': '',
            'TEST_VAR3': 'value3'
        }, clear=False):
            keys = ['TEST_VAR1', 'TEST_VAR2', 'TEST_VAR3']
            result = collect_environment_variables(keys)
            
            expected = {
                'TEST_VAR1': 'value1',
                'TEST_VAR3': 'value3'
            }
            self.assertEqual(result, expected)

    def test_collect_environment_variables_filters_whitespace_only(self):
        """Test that whitespace-only strings are filtered out."""
        with patch.dict(os.environ, {
            'TEST_VAR1': 'value1',
            'TEST_VAR2': '   ',
            'TEST_VAR3': '\t\n',
            'TEST_VAR4': 'value4'
        }, clear=False):
            keys = ['TEST_VAR1', 'TEST_VAR2', 'TEST_VAR3', 'TEST_VAR4']
            result = collect_environment_variables(keys)
            
            expected = {
                'TEST_VAR1': 'value1',
                'TEST_VAR4': 'value4'
            }
            self.assertEqual(result, expected)

    def test_collect_environment_variables_deduplicates_keys(self):
        """Test that duplicate keys in the input list are deduplicated."""
        with patch.dict(os.environ, {
            'TEST_VAR1': 'value1',
            'TEST_VAR2': 'value2'
        }, clear=False):
            # Duplicate keys in the input
            keys = ['TEST_VAR1', 'TEST_VAR2', 'TEST_VAR1', 'TEST_VAR2']
            result = collect_environment_variables(keys)
            
            expected = {
                'TEST_VAR1': 'value1',
                'TEST_VAR2': 'value2'
            }
            self.assertEqual(result, expected)

    def test_collect_environment_variables_preserves_order(self):
        """Test that the order of keys is preserved after deduplication."""
        with patch.dict(os.environ, {
            'TEST_VAR1': 'value1',
            'TEST_VAR2': 'value2',
            'TEST_VAR3': 'value3'
        }, clear=False):
            keys = ['TEST_VAR3', 'TEST_VAR1', 'TEST_VAR2', 'TEST_VAR3']
            result = collect_environment_variables(keys)
            
            # dict.fromkeys() preserves order in Python 3.7+
            expected_keys = ['TEST_VAR3', 'TEST_VAR1', 'TEST_VAR2']
            self.assertEqual(list(result.keys()), expected_keys)

    def test_collect_environment_variables_empty_input(self):
        """Test with empty input list."""
        result = collect_environment_variables([])
        self.assertEqual(result, {})

    def test_collect_environment_variables_mixed_scenarios(self):
        """Test a mixed scenario with valid, invalid, and missing variables."""
        with patch.dict(os.environ, {
            'VALID_VAR': 'valid_value',
            'EMPTY_VAR': '',
            'WHITESPACE_VAR': '  \t  ',
            'ANOTHER_VALID_VAR': 'another_value'
        }, clear=False):
            keys = [
                'VALID_VAR',
                'EMPTY_VAR', 
                'WHITESPACE_VAR',
                'MISSING_VAR',  # Not in environment
                'ANOTHER_VALID_VAR',
                'VALID_VAR'  # Duplicate
            ]
            result = collect_environment_variables(keys)
            
            expected = {
                'VALID_VAR': 'valid_value',
                'ANOTHER_VALID_VAR': 'another_value'
            }
            self.assertEqual(result, expected)

    def test_collect_environment_variables_with_actual_agent_keys(self):
        """Test with the actual environment variable keys used by the agent."""
        with patch.dict(os.environ, {
            'ROOT_AGENT_MODEL': 'gemini-2.0-flash-exp',
            'ANALYTICS_AGENT_MODEL': 'gemini-1.5-pro',
            'BQ_DATASET_ID': 'test_dataset',
            'BQ_PROJECT_ID': 'test_project',
            'EMPTY_VAR': '',  # This should be filtered out
        }, clear=False):
            keys = [
                'ROOT_AGENT_MODEL',
                'ANALYTICS_AGENT_MODEL',
                'BASELINE_NL2SQL_MODEL',  # Missing, should be filtered
                'BQ_DATASET_ID',
                'BQ_PROJECT_ID',
                'EMPTY_VAR',  # Empty, should be filtered
                'MISSING_VAR'  # Missing, should be filtered
            ]
            result = collect_environment_variables(keys)
            
            expected = {
                'ROOT_AGENT_MODEL': 'gemini-2.0-flash-exp',
                'ANALYTICS_AGENT_MODEL': 'gemini-1.5-pro',
                'BQ_DATASET_ID': 'test_dataset',
                'BQ_PROJECT_ID': 'test_project'
            }
            self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()