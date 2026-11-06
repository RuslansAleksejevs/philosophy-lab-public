#!/usr/bin/env python3
"""Synthetic smoke checks; intentionally distinct from actual provider capture."""
import argparse
from pathlib import Path
import sys
import unittest

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--smoke', action='store_true')
parser.add_argument('--no-report', action='store_true')
parser.parse_args()
root = Path(__file__).resolve().parents[1]
suite = unittest.defaultTestLoader.discover(str(root / 'tests'), pattern='test_*.py')
result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(not result.wasSuccessful())
