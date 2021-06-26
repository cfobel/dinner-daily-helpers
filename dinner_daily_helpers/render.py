from __future__ import division, print_function, unicode_literals

from typing import Optional
from pathlib import Path
from pydantic import ValidationError
import argparse
import enum
import io
import json
import os
import pathlib
import subprocess as sp
import sys

import jinja2
import numpy
import pandas as pd

from .menu import extract_menu, ingredients_table
from .types.week import Week
from .types.legacy import LegacyMenu, to_legacy

__all__ = ["RenderFormat", "load_legacy_menu", "render"]

PARENT_DIR = os.path.realpath(os.path.join(__file__, os.path.pardir))


class RenderFormat(str, enum.Enum):
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"


def render(
    menu: LegacyMenu,
    format_: Optional[RenderFormat] = RenderFormat.MARKDOWN,
) -> str:
    with io.StringIO() as output:
        if format_ == RenderFormat.JSON:
            # Dump as JSON output.
            return json.dumps(menu, indent=4, sort_keys=True)
        else:
            menu_markdown = io.StringIO()

            templates_dir = pathlib.Path(os.path.join(PARENT_DIR, "templates"))
            template_path = templates_dir.joinpath("weekly_menu.template.md")
            with open(template_path, "r") as input_:
                template = jinja2.Template(input_.read())

            df_ingredients = ingredients_table(menu.dict())

            print(
                template.render(menu=menu.dict(), df_ingredients=df_ingredients),
                file=menu_markdown,
            )

            if format_ == RenderFormat.MARKDOWN:
                return menu_markdown.getvalue()
            else:
                markdown_str = menu_markdown.getvalue().encode("utf8")
                # Dump as HTML.
                command = [
                    "pandoc",
                    "-f",
                    "gfm",
                    "-t",
                    "html",
                    "-",
                    "--template",
                    templates_dir.joinpath("GitHub.html5"),
                    "--toc",
                    "--toc-depth",
                    "2",
                ]
                process = sp.Popen(command, stdout=sp.PIPE, stdin=sp.PIPE)
                process.stdin.write(markdown_str)
                stdout, stderr = process.communicate()

                return stdout.strip()


def load_legacy_menu(source_path: Path) -> LegacyMenu:
    if source_path.suffix.lower() == ".json":
        try:
            menu = LegacyMenu.parse_file(source_path)
        except ValidationError as exception:
            week = Week.parse_file(source_path)
            menu = to_legacy(week.menu)
    else:
        with source_path.open("r") as input_:
            menu_html = input_.read()
        menu = LegacyMenu.parse_obj(extract_menu(menu_html))
    return menu
