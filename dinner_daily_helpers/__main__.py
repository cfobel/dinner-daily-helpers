from __future__ import division, print_function, unicode_literals

import argparse
import enum
import io
import json
import os
import pathlib
import subprocess as sp
import sys
from pathlib import Path
from typing import Optional

import jinja2
import pandas as pd
from pydantic import ValidationError

from .menu import extract_menu, ingredients_table
from .render import RenderFormat, load_legacy_menu, render
from .types.legacy import LegacyMenu, to_legacy
from .types.week import Week

PARENT_DIR = os.path.realpath(os.path.join(__file__, os.path.pardir))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "source",
        help="A (legacy) weekly menu HTML document, a JSON LegacyMenu, or a JSON Week.",
    )
    parser.add_argument(
        "output_path",
        default="-",
        help="Output path " "(default: write to `stdout`)",
        nargs="?",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--markdown", action="store_true")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.json:
        format_ = RenderFormat.JSON
    elif args.markdown:
        format_ = RenderFormat.MARKDOWN
    else:
        format_ = RenderFormat.HTML

    source_path = Path(args.source)
    menu = load_legacy_menu(source_path)
    rendered = render(menu, format_=format_)
    rendered_str = rendered.decode("utf8")

    if args.output_path == "-":
        print(rendered_str)
    else:
        with open(args.output_path, "w") as output:
            output.write(rendered_str)
