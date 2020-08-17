# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
import sys

from cppcheck_map_html.cli import main

if __name__ == "__main__":  # pragma: no cover
    sys.exit(main(sys.argv[1:]))
