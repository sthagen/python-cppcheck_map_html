# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,unused-import,reimported
import pytest  # type: ignore

import cppcheck_map_html.cli as cli


def test_main_nok_empty_array(capsys):
    job = ['[]']
    usage_feedback = (
        'Usage: script project repo branch commit < text_report > html_report\n'
        "Received (['[]']) argument vector"
    )
    assert cli.main(job) == 2
    out, err = capsys.readouterr()
    assert out.strip() == usage_feedback
