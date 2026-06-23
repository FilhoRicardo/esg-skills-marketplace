#!/usr/bin/env python3
"""Wrapper that runs local_review then submission_publisher in sequence.

Called by launchd every 30 seconds. Exits 0 if nothing to do or review
succeeded and publish succeeded. Exits non-zero on any failure.
"""
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import local_review
import submission_publisher

rc = local_review.main()
if rc != 0:
    sys.exit(rc)
sys.exit(submission_publisher.main())
