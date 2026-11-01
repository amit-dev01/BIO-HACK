"""Pytest configuration ensuring isolated test environments."""

import os

# Ensure unit tests run in mock mode without requiring external live satellite credentials
os.environ["MOCK_MODE"] = "true"

