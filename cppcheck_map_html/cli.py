# -*- coding: utf-8 -*-
# pylint: disable=line-too-long
"""Add logical documentation here later TODO."""
import os
import sys

from cppcheck_map_html.cppcheck_map_html import process

DEBUG = os.getenv("CPPCHECK_MH_DEBUG")


# pylint: disable=expression-not-assigned
def main(argv=None):
    """Process ... TODO."""
    argv = sys.argv[1:] if argv is None else argv
    return process(argv)
