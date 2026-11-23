"""Build a Jupyter notebook from a percent-format Python source.

Usage: python build_nb.py SOURCE.py OUTPUT.ipynb [--allow-comments] [--python 3.11]

Cells:
  # %%               starts a code cell
  # %% [markdown]    starts a markdown cell; each line is written as '# text'

Checks: every code cell must parse; code cells may not contain '#' comments unless --allow-comments;
markdown with em dashes or emoji triggers a warning.
"""
import argparse
import ast
import re
import sys
from pathlib import Path

try:
    import nbformat
    from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook
except ImportError:
    sys.exit("nbformat is required: pip install nbformat")

EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")


def has_comment(code):
    import io
    import tokenize
    try:
        return any(t.type == tokenize.COMMENT for t in tokenize.generate_tokens(io.StringIO(code).readline))
    except tokenize.TokenError:
        return bool(re.search(r"^\s*#", code, flags=re.M))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source")
    ap.add_argument("output")
    ap.add_argument("--allow-comments", action="store_true")
    ap.add_argument("--python", default="3.11")
    a = ap.parse_args()

    src = Path(a.source).read_text(encoding="utf-8")
    chunks = re.split(r"^# %%(.*)$", src, flags=re.M)
    if len(chunks) < 3:
        sys.exit("no '# %%' cell markers found")
    cells, warnings = [], []
    for i in range(1, len(chunks), 2):
        tag, body = chunks[i].strip(), chunks[i + 1].strip("\n")
        if tag == "[markdown]":
            text = "\n".join(line[2:] if line.startswith("# ") else line.lstrip("#") for line in body.splitlines()).strip()
            if "—" in text:
                warnings.append(f"markdown cell {len(cells)}: em dash")
            if EMOJI.search(text):
                warnings.append(f"markdown cell {len(cells)}: emoji")
            cells.append(new_markdown_cell(text))
        else:
            code = body.rstrip() + "\n"
            try:
                ast.parse(code)
            except SyntaxError as e:
                sys.exit(f"syntax error in code cell {len(cells)}: {e}")
            if not a.allow_comments and has_comment(code):
                sys.exit(f"comment found in code cell {len(cells)} (use --allow-comments to permit)")
            cells.append(new_code_cell(code.rstrip("\n")))
    nb = new_notebook(cells=cells, metadata={
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": a.python},
    })
    nbformat.validate(nb)
    nbformat.write(nb, a.output)
    for w in warnings:
        print("warning:", w)
    print(f"{a.output}: {len(cells)} cells ({sum(c.cell_type == 'code' for c in cells)} code)")


if __name__ == "__main__":
    main()
