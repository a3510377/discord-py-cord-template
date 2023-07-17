from __future__ import annotations

import ast
import inspect
import io
import re
import sys
import time
import tokenize
from pathlib import Path
from typing import Any

import click
from polib import POEntry, POFile, pofile

KEYWORDS = ("_",)
KEYWORDS_KEYWORDS = (
    "local",
    "all",
    "guild_local",
)
DECORATOR_NAMES = ("cog_i18n",)
DECORATOR_NAMES_CLASS_KWARGS = (
    "name",
    "description",
)
USE_FORMAT_STR = re.compile(
    r"{{|}}|{\w*(\.[a-zA-Z_]\w*|"
    r"\[[^\]'\"]+\])*(![rsa])?(:\w?[><=^]?[ +-]?#?\d*,?(\.\d+)?[bcdeEfFgGnosxX%]?)?}|"
    r"%(\([\w\s]*\))?[-+#0]*(\d+|\*)?(\.(\d+|\*))?([hlL])?[diouxXeEfFgGcrsab%]"
)

__version__ = "1.0.0"


class POTFileManager:
    def __init__(self, **kwargs: Any) -> None:
        """
        `output_dir`
        `relative_cwd`
        """
        self.current_file: Path | None = None
        self.potfile: POFile | None = None

        self.out_dir = kwargs.pop("output_dir", "locales")

        self.relative_cwd = kwargs.pop("relative_cwd", False)

        self._potfiles: dict[Path, POFile] = {}

    def move_to_current_file(self, path: Path | str) -> None:
        self.current_file = Path(path)

        current_dir = Path() if self.relative_cwd else self.current_file.parent

        self._out_dir = current_dir / self.out_dir
        if self._out_dir not in self._potfiles:
            self.potfile: POFile = POFile()
            self._potfiles[self._out_dir] = self.potfile
            self.potfile.metadata = self.potfile_metadata()

    @staticmethod
    def potfile_metadata() -> dict[str, str]:
        # https://www.gnu.org/software/gettext/manual/gettext.html
        return {
            "Project-Id-Version": "PACKAGE VERSION",
            "Report-Msgid-Bugs-To": "FULL NAME <EMAIL@ADDRESS>",
            "POT-Creation-Date": time.strftime("%Y-%m-%d %H:%M%z"),
            "PO-Revision-Date": "YEAR-MO-DA HO:MI+ZONE",
            "Last-Translator": "FULL NAME <EMAIL@ADDRESS>",
            "Language-Team": "FULL NAME <EMAIL@ADDRESS>",
            "Language": "LANGUAGE",
            "MIME-Version": "1.0",
            "Content-Type": "text/plain; charset=UTF-8",
            "Content-Transfer-Encoding": "8bit",
            "Generated-By": f"dpy-template {__version__}",
        }

    @classmethod
    def from_file(cls, path: str, **kwargs) -> POTFileManager:
        return cls(
            current_file=path,
            **kwargs,
        )

    def write(self, langs: list[str] = "zh-TW", overwrite: bool = False) -> None:
        for outfile_path, potfile in self._potfiles.items():
            for lang in langs:
                current_file = outfile_path / f"{lang}.po"

                potfile.metadata |= {"Language": lang}

                old_potfile = potfile
                if not overwrite and current_file.is_file():
                    old_potfile = pofile(current_file)
                    old_potfile.merge(potfile)

                if not old_potfile[:]:
                    continue
                current_file.parent.mkdir(parents=True, exist_ok=True)

                def sort(e: POEntry):
                    try:
                        path, line = e.occurrences[0]
                    except IndexError:
                        return ()

                    # int is needed, sometimes he returns str type and throws an error
                    return (path, int(line))

                old_potfile.sort(key=sort)
                old_potfile.save(str(current_file))

                print(f"summon {current_file} done")

    def add_entry(
        self,
        id: str,
        comments: list[str] | str | None = None,
        *,
        lineno: int,
        is_docstring: bool = False,
    ) -> None:
        if self.current_file is None:
            raise RuntimeError("pot file 未設定")

        if not id:
            return

        entry = self.potfile.find(id)
        flags = ["docstring"] if is_docstring else []
        occurrence = (str(self.current_file), lineno)

        comment = ""
        if comments:
            comment = "\n".join(comments) if isinstance(comments, list) else comments

        if USE_FORMAT_STR.search(id):
            flags.append("python-format")

        if entry is None:
            self.potfile.append(
                POEntry(
                    msgid=id,
                    comment=comment,
                    occurrences=[occurrence],
                    flags=flags,
                )
            )
        else:
            if not entry.comment:
                entry.comment = comment
            elif comment:
                entry.comment = f"{entry.comment}\n{comment}"
            if not entry.flags:
                entry.flags = flags

            if occurrence not in entry.occurrences:
                entry.occurrences.append(occurrence)
            entry.occurrences.sort()


class ContentExtractor(ast.NodeVisitor):
    COMMENT_RE = re.compile(r"[\t ]*(#(?P<comment>.*))?")

    def __init__(self, source: str, **kwargs: Any) -> None:
        self.pot_file: POTFileManager = kwargs.pop("pot_file", POTFileManager(**kwargs))
        self.source = source
        self.file_comments: dict[int, str] = {}  # {line_number: comment}
        self.get_comments()

    @classmethod
    def from_file(cls, path: Path | str, **kwargs: Any) -> ContentExtractor:
        source = Path(path).read_text(encoding="utf-8")
        self = cls(source, current_file=path, **kwargs)

        self.visit(ast.parse(source))

        return self

    def error(self, starting_node: ast.AST, msg: str) -> None:
        print(
            f"{self.pot_file.current_file}:{starting_node.lineno}: {msg}\n"
            + inspect.cleandoc(
                ast.get_source_segment(
                    self.source,
                    starting_node,
                    padded=True,
                )
            ),
            file=sys.stderr,
        )

    def get_literal_string(self, node: ast.AST) -> ast.Constant | None:
        return (
            node
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
            else None
        )

    def get_node_class_locals(self, node: ast.ClassDef) -> list[ast.Constant]:
        for deco in node.decorator_list:
            if isinstance(deco, ast.Call):  # @class_def()
                if deco.func.id in DECORATOR_NAMES:
                    break
            elif isinstance(deco, ast.Name):  # @class_def
                if deco.id in DECORATOR_NAMES:
                    break
        else:
            self.generic_visit(node)
            return []

        result = []
        for k in node.keywords:
            if k.arg in DECORATOR_NAMES_CLASS_KWARGS:
                result.append(k.value)

        if isinstance(body := node.body[0], ast.Expr):
            result.append(self.get_literal_string(body.value))

        return [d for d in result if d]

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        # self.add_entry(node, comments=comments, starting_node=node)
        for docs in self.get_node_class_locals(node):
            self.add_entry(docs)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name):
            if node.func.id not in KEYWORDS:
                return self.generic_visit(node)
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr not in KEYWORDS:
                return self.generic_visit(node)
        else:
            return self.generic_visit(node)

        if len(node.args) != 1 or len(
            [x for x in node.keywords if x.arg not in KEYWORDS_KEYWORDS]
        ):
            self.error(node, "發現錯誤的參數")
            return self.generic_visit(node)

        arg = node.args[0]

        if string_node := self.get_literal_string(arg):
            comments, tmp_line = [], -1
            for node in (node, string_node):
                if tmp_line == (lineno := node.lineno):
                    comments.extend(self.get_comment(lineno))
                tmp_line = lineno
            self.add_entry(string_node, comments=comments, starting_node=node)
        else:
            self.error(node, "輸入了錯誤的參數")

        self.generic_visit(node)

    def add_entry(
        self,
        node: ast.Constant,
        comments: list[str] | str | None = None,
        starting_node: ast.AST | None = None,
        is_docstring: bool = False,
    ) -> None:
        self.pot_file.add_entry(
            inspect.cleandoc(node.value),
            comments=comments,
            lineno=(starting_node or node).lineno,
            is_docstring=is_docstring,
        )

    def get_comments(self) -> None:
        for type, data, loc, _, _ in tokenize.tokenize(
            io.BytesIO(self.source.encode(encoding="utf-8")).readline
        ):
            if type is tokenize.COMMENT:
                self.file_comments[loc[0]] = data.removeprefix("#").strip()

    def get_comment(self, line_number: int) -> list[str] | None:
        comments = []

        line_number -= 1
        while comment := self.file_comments.get(line_number):
            comments.append(comment)
            line_number -= 1

        comments.sort()
        return comments


def show_version(ctx: click.Context, _: click.Parameter, value: Any):
    if not value or ctx.resilient_parsing:
        return
    click.echo("Version 1.0")
    ctx.exit()


@click.command()
@click.option(
    "-f",
    "arg_include_paths",
    help="include paths",
    multiple=True,
    type=Path,
)
@click.option(
    "-e",
    "arg_excluded_glob",
    help="set excluded glob",
    default=[],
    multiple=True,
    type=str,
)
@click.option(
    "-v",
    "--version",
    help="show version",
    expose_value=False,
    is_eager=True,
    is_flag=True,
    callback=show_version,
)
@click.option("-r", "recursive", help="use recursive", is_flag=True)
@click.option("-l", "lang", help="output lang", default="zh-TW", type=str)
@click.option("-o", "overwrite", help="overwrite old po file", is_flag=True)
def main_command(**kwargs):
    return main(**kwargs)


def main(
    arg_include_paths: list[Path] = [],
    arg_excluded_glob: list[str] = [],
    recursive=True,
    lang: str = "zh-TW",
    overwrite: bool = False,
) -> None:
    include_paths: list[Path] = []

    for path in arg_include_paths:
        if path.is_dir():
            include_paths.extend(path.glob("**/*.py" if recursive else "*.py"))
        else:
            include_paths.append(path)

    for glob in arg_excluded_glob:
        excluded_files = set(Path().glob(glob))
        include_paths = [f for f in include_paths if f not in excluded_files]

    potfile_manager = POTFileManager()
    for path in include_paths:
        potfile_manager.move_to_current_file(path)
        ContentExtractor.from_file(path, pot_file=potfile_manager)

    potfile_manager.write(langs=lang.split(","), overwrite=overwrite)


if __name__ == "__main__":
    main_command()
