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

"""Test cases for environment variable filtering functionality only."""

import os
import logging
from unittest.mock import patch

# Set up basic logging for the test
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def collect_environment_variables(env_var_keys: list[str]) -> dict[str, str]:
    """
    Collect environment variables, filtering out None, empty, or whitespace-only values.
    
    Args:
        env_var_keys: List of environment variable keys to collect.
        
    Returns:
        Dictionary containing only environment variables with valid values.
        
    Note:
        This function also deduplicates the input keys and logs which variables
        are included or skipped during collection.
    """
    # Deduplicate the environment variable keys
    unique_keys = list(dict.fromkeys(env_var_keys))
    if len(unique_keys) != len(env_var_keys):
        logger.info("Deduplicated %d environment variable keys to %d unique keys", 
                   len(env_var_keys), len(unique_keys))
    
    env_vars = {}
    included_vars = []
    skipped_vars = []
    
    for key in unique_keys:
        value = os.getenv(key)
        
        # Filter out None, empty, or whitespace-only values
        if value is not None and value.strip():
            env_vars[key] = value
            included_vars.append(key)
        else:
            skipped_vars.append(key)
    
    # Log the results
    if included_vars:
        logger.info("Including %d environment variables: %s", 
                   len(included_vars), ", ".join(included_vars))
    
    if skipped_vars:
        logger.info("Skipping %d environment variables (None/empty/whitespace): %s", 
                   len(skipped_vars), ", ".join(skipped_vars))
    
    return env_vars


def test_filtering_functionality():
    """Test the environment variable filtering functionality."""
    print("Running environment variable filtering tests...")
    
    # Test 1: Valid values
    print("\nTest 1: Valid values")
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
        assert result == expected, f"Expected {expected}, got {result}"
        print("✓ Valid values test passed")

    # Test 2: Filter None values
    print("\nTest 2: Filter None values")
    with patch.dict(os.environ, {
        'TEST_VAR1': 'value1',
        'TEST_VAR2': 'value2'
    }, clear=False):
        keys = ['TEST_VAR1', 'TEST_VAR2', 'TEST_VAR3']  # TEST_VAR3 not in env
        result = collect_environment_variables(keys)
        expected = {
            'TEST_VAR1': 'value1',
            'TEST_VAR2': 'value2'
        }
        assert result == expected, f"Expected {expected}, got {result}"
        print("✓ None values filter test passed")

    # Test 3: Filter empty strings
    print("\nTest 3: Filter empty strings")
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
        assert result == expected, f"Expected {expected}, got {result}"
        print("✓ Empty strings filter test passed")

    # Test 4: Filter whitespace-only strings
    print("\nTest 4: Filter whitespace-only strings")
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
        assert result == expected, f"Expected {expected}, got {result}"
        print("✓ Whitespace-only strings filter test passed")

    # Test 5: Deduplicate keys
    print("\nTest 5: Deduplicate keys")
    with patch.dict(os.environ, {
        'TEST_VAR1': 'value1',
        'TEST_VAR2': 'value2'
    }, clear=False):
        keys = ['TEST_VAR1', 'TEST_VAR2', 'TEST_VAR1', 'TEST_VAR2']
        result = collect_environment_variables(keys)
        expected = {
            'TEST_VAR1': 'value1',
            'TEST_VAR2': 'value2'
        }
        assert result == expected, f"Expected {expected}, got {result}"
        print("✓ Deduplication test passed")

    # Test 6: Mixed scenario
    print("\nTest 6: Mixed scenario")
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
        assert result == expected, f"Expected {expected}, got {result}"
        print("✓ Mixed scenario test passed")

    print("\n✅ All tests passed successfully!")


if __name__ == "__main__":
    test_filtering_functionality()