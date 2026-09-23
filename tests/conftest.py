"""Shared pytest configuration: Hypothesis profiles (dev/ci)."""

import os

from hypothesis import HealthCheck, settings

settings.register_profile("dev", max_examples=100)
settings.register_profile(
    "ci", max_examples=500, derandomize=True, suppress_health_check=[HealthCheck.too_slow]
)
settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "dev"))
