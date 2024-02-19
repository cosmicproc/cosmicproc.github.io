import shutil
import subprocess
from itertools import chain
from pathlib import Path

import markdown
import minify_html
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pygments.formatters.html import HtmlFormatter

import config


class Paths:
    STATIC = Path("static")
    OUTPUT = Path("output")
    TEMPLATES = Path("templates")
    CONTENT = Path("content")


jinja_env = Environment(loader=FileSystemLoader(Paths.TEMPLATES), autoescape=select_autoescape())
jinja_env.globals["config"] = config


def render_and_write(template, path, **context):
    """
    Render template and write it to the given path.
    """
    with open(path, "w") as f:
        f.write(jinja_env.get_template(template).render(FILE_NAME=path.name, **context))


def minify_css(css):
    """
    Minify the given css string using lightningcss.
    Expects lightningcss to be installed and callable through npx.
    Otherwise, returns the given css as it is.
    """
    process = subprocess.run(["npx", "lightningcss", "-m"], input=css, capture_output=True, text=True)
    return process.stdout if process.returncode == 0 else css


def main():
    # Clear the output directory
    try:
        shutil.rmtree(Paths.OUTPUT)
    except FileNotFoundError:
        pass

    # Copy and paste the static files
    shutil.copytree(Paths.STATIC, Paths.OUTPUT / "static")

    # Generate highlight.css
    highlight_light = HtmlFormatter(style="default").get_style_defs()
    highlight_dark = HtmlFormatter(style="monokai").get_style_defs()
    render_and_write("highlight.css", Paths.OUTPUT / "static/css/highlight.css",
                     highlight_light=highlight_light,
                     highlight_dark=highlight_dark)

    jinja_env.globals["STYLESHEETS"] = list(
        i.relative_to(Paths.OUTPUT) for i in (Paths.OUTPUT / "static/css").glob("*.css"))

    md = markdown.Markdown(extensions=["fenced_code", "codehilite", "smarty", "meta"])

    # Generate pages
    posts = []
    for page in Paths.CONTENT.glob("*.md"):
        if page.stem != "index":
            with open(page) as f:
                content = md.convert(f.read())
            if not md.Meta.get("not_a_post", False):
                posts.append({"title": md.Meta.get("title", [page.stem])[0], "address": page.stem})
            render_and_write("base.html", Paths.OUTPUT / (page.stem + ".html"), content=content, META=md.Meta)

    # Generate the homepage
    with open(Paths.CONTENT / "index.md") as f:
        content = md.convert(f.read())
    render_and_write("base.html", Paths.OUTPUT / "index.html", content=content, META=md.Meta, HOME_PAGE=True,
                     POSTS=posts)

    # Minify files
    minifiers = {
        "html": minify_html.minify,
        "css": minify_css,
    }
    target_files = chain(*(Paths.OUTPUT.rglob("*." + i) for i in minifiers.keys()))
    for file in target_files:
        if file.is_file():
            with open(file, "r+") as f:
                data = f.read()
                f.seek(0)
                f.write(minifiers[file.suffix[1:]](data))
                f.truncate()


if __name__ == '__main__':
    main()
