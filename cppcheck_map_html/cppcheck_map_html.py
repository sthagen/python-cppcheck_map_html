# -*- coding: utf-8 -*-
# pylint: disable=line-too-long
"""Transform and Retarget the cppcheck text output for errors and warnings into HTML page.

Parse the lines following the pattern:

[local_path:line_number]: (level) finding

Map to:

{base_url}projects/{project}/repos/{repo}/browse/local_path?at=refs%2Fheads%2F{branch}}#{line_number}

with:

base_url = 'https://bitbucket.example.com/'
project = argument_project
repo = argument_repo
branch = argument_branch

Similarly relations denoted like:

[local_path_first:line_number_first] -> [local_path_last:line_number_last]: (level) finding

to:

{base_url}projects/{project}/repos/{repo}/browse/local_path_first?at=refs%2Fheads%2F{branch}}#{line_number_first}
and:
{base_url}projects/{project}/repos/{repo}/browse/local_path_last?at=refs%2Fheads%2F{branch}}#{line_number_last}



"""
import datetime as dti
import pathlib
import sys

PAGE_PREFIX = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Static Analysis</title>
  <meta name="description" content="Static code analysis.">
  <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
      html {font-family: Verdana, Arial, sans-serif;}
      a {color: #0c2d82;}
      b {font-weight: 600;}
      h1 {font-weight: 300; text-transform: capitalize;}
      h2 {font-weight: 200;}
      li {line-height: 1.5;}
      table {table-layout: fixed; width: 150%; background-color: #ffffff; margin: 20px; border-collapse: collapse;}
      td, th {word-wrap: break-word; border: solid 1px #666666;}
      th {background-color: #0c2d82; color: #ffffff; font-size: 75%; font-weight: 300;}
      td {vertical-align: top; font-size: 67%; padding: 2px;}
      table caption {font-size: 120%; margin-bottom: 20px;}
      tbody tr:nth-child(odd) {background-color: #dddddd;}
      tbody tr:nth-child(even) {background-color: #ffffff;}
      .no-decor {text-decoration: none;}
      .ta-center {text-align: center;}
      .ta-right {text-align: right;}
      .sp-err {color: white; background-color: darkred; font-size:75%;}
      .sp-info {color: white; background-color: blue; font-size:75%;}
      .sp-perf {color: white; background-color: magenta; font-size:75%;}
      .sp-perf-unsure {color: white; background-color: plum; font-size:75%;}
      .sp-port {color: black; background-color: cyan; font-size:75%;}
      .sp-style {color: white; background-color: forestgreen; font-size:75%;}
      .sp-style-unsure {color: gray; background-color: springgreen; font-size:75%;}
      .sp-warn {color: white; background-color: orangered; font-size:75%;}
      .sp-nn {color: purple; background-color: yellow; font-size:75%;}
      .ff-067 {font-family: Courier, fixed; font-size:67%;}
      .ff-075 {font-family: Courier, fixed; font-size:75%;}
      .finding {line-height: 1.0;}
    </style>
</head>
<body>
<header>
  <h1><a href="/static_analysis/" class="no-decor" target="_blank">Static Analysis</a></h1>
</header>
<main>
  <h2>Warnings &amp; Errors from Static Code Analysis</h2>
"""

PAGE_POSTFIX = """\
</main>
<footer>
  <address><b>Contact</b>: Given Family &lt;<a href="mailto:given.family@example.com">given.family@example.com</a>&gt;</address>
</footer>
</body>
</html>
"""

BASE_URL = 'https://bitbucket.example.com/'


def map_findings(stream, project, repo, commit):
    """Transform the findings (cf. doc string of module)."""
    job_warnings = []
    folder_memo = 'NOWHERE_LAND'
    level_prefix_map = {
        "error": '<span class="sp-err">',
        "information": '<span class="sp-info">',
        "style": '<span class="sp-style">',
        "performance": '<span class="sp-perf">',
        "portability": '<span class="sp-port">',
        "warning": '<span class="sp-warn">',
        "performance, inconclusive": '<span class="sp-perf-unsure">',
        "style, inconclusive": '<span class="sp-style-unsure">',
        "nn": '<span class="sp-nn">',
    }
    for line in stream:
        record = line.strip()
        if not record:
            continue
        # Most records follow single line pattern:
        # [local_path:line_number]: (level) finding
        try:
            address_part, rest = record.split("]: (", 1)
        except ValueError:
            job_warnings.append(record)
            continue
        try:
            local_path, line_number = address_part.lstrip("[").split(":", 1)
        except ValueError:
            job_warnings.append(record)
            continue

        if "[" in line_number:  # We have a range, back off
            # [local_path:line_number_first] -> [local_path:line_number_last]: (level) finding
            address_parts, rest = record.split("]: (", 1)
            # [local_path:line_number_first] -> [local_path:line_number_last
            left, right = address_parts.lstrip("[").split("] -> [", 1)
            left_path, left_number = left.split(":", 1)
            right_path, right_number = right.split(":", 1)
            if not left_path.startswith(folder_memo):
                folder_memo = f'{"/".join(pathlib.Path(left_path).parts[:-1])}/'
                yield f'<h2>{folder_memo}</h2>'
            left_display = f'{left_path.replace(folder_memo, "")}:{left_number}'
            right_display = f'{right_path.replace(folder_memo, "")}:{right_number}'
            try:
                level, finding = rest.split(") ", 1)
            except ValueError:
                job_warnings.append(record)
                continue
            level_display = f'{level_prefix_map.get(level, level_prefix_map["nn"])}{level}</span>'
            left_url = f'{BASE_URL}projects/{project}/repos/{repo}/browse/{left_path}?at={commit}#{left_number}'
            right_url = f'{BASE_URL}projects/{project}/repos/{repo}/browse/{right_path}?at={commit}#{right_number}'
            left_link = f'[<a href="{left_url}" class="no-decor">{left_display}</a>]'
            right_link = f'[<a href="{right_url}" class="no-decor">{right_display}</a>]'
            yield f'<p class="finding"><span class="ff-075">{left_link} -&gt; {right_link}: </span>{level_display}<span class="ff-075"> {finding}</span></p>'
            continue

        if not local_path.startswith(folder_memo):
            folder_memo = f'{"/".join(pathlib.Path(local_path).parts[:-1])}/'
            yield f'<h2>{folder_memo}</h2>'
        path_display = f'{local_path.replace(folder_memo, "")}:{line_number}'
        try:
            level, finding = rest.split(") ", 1)
        except ValueError:
            job_warnings.append(record)
            continue
        level_display = f'{level_prefix_map.get(level, level_prefix_map["nn"])}{level}</span>'
        the_url = f'{BASE_URL}projects/{project}/repos/{repo}/browse/{local_path}?at={commit}#{line_number}'
        the_link = f'[<a href="{the_url}" class="no-decor">{path_display}</a>]'
        yield f'<p class="finding"><span class="ff-075">{the_link}: </span>{level_display}<span class="ff-075"> {finding}</span></p>'

    if job_warnings:
        nl = "\n"
        yield f'<h2>Warnings from Job Execution</h2><pre>{nl.join(job_warnings)}</pre>'


def process(argv=None):
    """Do the mapping."""
    if len(argv) != 4:
        print(f"Usage: script project repo branch commit < text_report > html_report")
        print(f"Received ({argv}) argument vector")
        return 2

    project, repo, branch, commit = argv
    print(PAGE_PREFIX)
    print(f"<p>Report generated for {project}.{repo}[{branch}].at({commit}) {dti.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>")
    for finding in map_findings(sys.stdin, project, repo, commit):
        print(finding)
    print(PAGE_POSTFIX)
    return 0
