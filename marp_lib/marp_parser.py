"""Parse the repository-owned, supported Marp Markdown subset into native objects."""

# Standard Library
import pathlib
import re
from dataclasses import dataclass

# PIP3 modules
import yaml
from markdown_it import MarkdownIt
from markdown_it.token import Token

# Local Modules
import marp_lib.native_model
from marp_lib import layouts


LAYOUT_CLASSES = frozenset(layouts.LAYOUTS)
FRONT_MATTER_KEYS = frozenset(("marp", "theme", "size", "paginate", "title"))
COMMENT_PATTERN = re.compile(r"<!--(.*?)-->", re.DOTALL)
FENCE_PATTERN = re.compile(r"^\s*(`{3,}|~{3,})")
DIVIDER_PATTERN = re.compile(r"^ {0,3}---\s*$")
BACKGROUND_IMAGE_PATTERN = re.compile(r"!\[\s*(?:bg|background)(?:\s|\]|$)", re.IGNORECASE)
UNSUPPORTED_DIRECTIVE_PATTERN = re.compile(
	r"^(?:class|paginate|theme|size|background(?:-|_)?[a-z]*):", re.IGNORECASE)


class MarpParseError(ValueError):
	"""Report an actionable canonical-source parsing error."""


class UniqueKeyLoader(yaml.SafeLoader):
	"""Safe YAML loader that exposes duplicate author keys as source errors."""


#============================================
def construct_unique_mapping(loader: UniqueKeyLoader, node: yaml.MappingNode,
		deep: bool = False) -> dict[object, object]:
	"""Construct one mapping while rejecting a duplicate key."""
	mapping: dict[object, object] = {}
	for key_node, value_node in node.value:
		key = loader.construct_object(key_node, deep=deep)
		if key in mapping:
			raise yaml.constructor.ConstructorError("while constructing a mapping", node.start_mark,
				f"found duplicate key {key!r}", key_node.start_mark)
		mapping[key] = loader.construct_object(value_node, deep=deep)
	return mapping


UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
	construct_unique_mapping)


#============================================
def error(path: pathlib.Path, line: int, message: str) -> MarpParseError:
	"""Create the parser's uniformly actionable error value."""
	return MarpParseError(f"{path}:{line}: {message}")


#============================================
def location(path: pathlib.Path, line: int) -> marp_lib.native_model.SourceLocation:
	"""Build retained source provenance for one parsed item."""
	return marp_lib.native_model.SourceLocation(path, line)


#============================================
def parse_front_matter(path: pathlib.Path, source: str) -> tuple[dict[str, object], str, int]:
	"""Parse strict opening YAML and return its body with physical start line."""
	if source.startswith("\ufeff"):
		source = source.removeprefix("\ufeff")
	if not source.startswith("---\n"):
		raise error(path, 1, "Marp Markdown must begin with an opening YAML '---' line")
	closing = re.search(r"^---\s*$", source[4:], re.MULTILINE)
	if closing is None:
		raise error(path, 1, "opening YAML front matter is not closed")
	front_end = 4 + closing.start()
	front_text = source[4:front_end]
	body_start = 4 + closing.end()
	if source[body_start:body_start + 1] == "\n":
		body_start += 1
	try:
		loaded = yaml.load(front_text, Loader=UniqueKeyLoader)
	except yaml.YAMLError as exc:
		line = getattr(getattr(exc, "problem_mark", None), "line", 0) + 2
		raise error(path, line, f"invalid YAML front matter: {exc.problem or str(exc)}") from exc
	if not isinstance(loaded, dict):
		raise error(path, 2, "front matter must be a YAML mapping")
	unknown = set(loaded) - FRONT_MATTER_KEYS
	if unknown:
		raise error(path, 2, f"unsupported front-matter key: {sorted(unknown)[0]}")
	if loaded.get("marp") is not True:
		raise error(path, 2, "front matter must declare 'marp: true'")
	if loaded.get("theme") != "genetics":
		raise error(path, 2, "front matter must declare 'theme: genetics'")
	if not re.search(r"^size:\s*(?:['\"]16:10['\"]|16:10)\s*$", front_text, re.MULTILINE):
		raise error(path, 2, "front matter must declare 'size: 16:10'")
	loaded["size"] = "16:10"
	paginate = loaded.get("paginate", True)
	if type(paginate) is not bool:
		raise error(path, 2, "front-matter paginate must be true or false")
	title = loaded.get("title", "")
	if not isinstance(title, str):
		raise error(path, 2, "front-matter title must be a string")
	body_line = source[:body_start].count("\n") + 1
	return loaded, source[body_start:], body_line


#============================================
def split_slides(path: pathlib.Path, body: str, start_line: int) -> list[tuple[str, int]]:
	"""Split only top-level page rulers, preserving fence and comment content."""
	slides: list[tuple[str, int]] = []
	lines = body.splitlines(keepends=True)
	current: list[str] = []
	line_number = start_line
	slide_line = start_line
	fence: str | None = None
	in_comment = False
	for line in lines:
		plain = line.rstrip("\r\n")
		fence_match = FENCE_PATTERN.match(plain)
		if not in_comment and fence_match is not None:
			marker = fence_match.group(1)
			if fence is None:
				fence = marker[0]
			elif marker[0] == fence:
				fence = None
		if fence is None and not in_comment and DIVIDER_PATTERN.match(plain):
			slides.append(("".join(current), slide_line))
			current = []
			slide_line = line_number + 1
		else:
			current.append(line)
		if "<!--" in line and "-->" not in line:
			in_comment = True
		if in_comment and "-->" in line:
			in_comment = False
		line_number += 1
	slides.append(("".join(current), slide_line))
	return slides


#============================================
def remove_comments(path: pathlib.Path, raw_slide: str, base_line: int,
		default_paginate: bool) -> tuple[str, str, bool, tuple[str, ...]]:
	"""Extract standalone directives and notes while retaining source line offsets."""
	layout_class: str | None = None
	paginate = default_paginate
	notes: list[str] = []
	def replace(match: re.Match[str]) -> str:
		nonlocal layout_class, paginate
		line = base_line + raw_slide[:match.start()].count("\n")
		before = raw_slide[raw_slide.rfind("\n", 0, match.start()) + 1:match.start()]
		after_end = raw_slide.find("\n", match.end())
		after = raw_slide[match.end():] if after_end == -1 else raw_slide[match.end():after_end]
		if before.strip() or after.strip():
			raise error(path, line, "HTML comments must occupy their own source line")
		comment = match.group(1).strip()
		if comment.startswith("_class:"):
			classes = comment.partition(":")[2].split()
			if len(classes) != 1:
				raise error(path, line, "_class must name exactly one canonical layout")
			if classes[0] not in LAYOUT_CLASSES:
				raise error(path, line, f"unsupported Marp slide class: {classes[0]}")
			if layout_class is not None:
				raise error(path, line, "slide declares _class more than once")
			layout_class = classes[0]
		elif comment.startswith("_paginate:"):
			value = comment.partition(":")[2].strip()
			if value not in ("true", "false"):
				raise error(path, line, "_paginate must be true or false")
			paginate = value == "true"
		elif comment.startswith("notes:"):
			notes.append(comment.removeprefix("notes:").strip())
		elif comment.startswith("ODP hidden slide skipped:"):
			pass
		elif comment.startswith("_") or UNSUPPORTED_DIRECTIVE_PATTERN.match(comment):
			raise error(path, line, f"unsupported Marp directive: {comment.splitlines()[0]}")
		elif comment:
			notes.append(comment.removeprefix("notes:").strip())
		return "\n" * match.group(0).count("\n")
	cleaned = COMMENT_PATTERN.sub(replace, raw_slide)
	if layout_class is None:
		raise error(path, base_line, "slide must declare exactly one canonical _class directive")
	return cleaned, layout_class, paginate, tuple(notes)


#============================================
def token_line(token: Token, base_line: int) -> int:
	"""Convert markdown-it's zero-based local token line into a physical line."""
	return base_line + token.map[0] if token.map is not None else base_line


#============================================
def parse_inlines(path: pathlib.Path, line: int, children: list[Token]) -> tuple[marp_lib.native_model.Inline, ...]:
	"""Convert supported markdown-it inline tokens into editable semantic runs."""
	result: list[marp_lib.native_model.Inline] = []
	index = 0
	while index < len(children):
		token = children[index]
		if token.type == "text":
			result.append(marp_lib.native_model.Text(token.content))
		elif token.type in ("softbreak", "hardbreak"):
			result.append(marp_lib.native_model.Break())
		elif token.type == "code_inline":
			result.append(marp_lib.native_model.InlineCode(token.content))
		elif token.type in ("strong_open", "em_open", "link_open"):
			close_type = token.type.replace("_open", "_close")
			depth = 1
			end = index + 1
			while end < len(children) and depth:
				if children[end].type == token.type:
					depth += 1
				elif children[end].type == close_type:
					depth -= 1
				end += 1
			if depth:
				raise error(path, line, f"unclosed inline token: {token.type}")
			inner = parse_inlines(path, line, children[index + 1:end - 1])
			if token.type == "strong_open":
				result.append(marp_lib.native_model.Strong(inner))
			elif token.type == "em_open":
				result.append(marp_lib.native_model.Emphasis(inner))
			else:
				url = token.attrGet("href")
				if url is None or not re.match(r"(?:https?://|mailto:)", url):
					raise error(path, line, "links must use an absolute http, https, or mailto URL")
				result.append(marp_lib.native_model.Link(inner, url))
			index = end - 1
		elif token.type == "image":
			raise error(path, line, "images must be standalone component-image blocks")
		else:
			raise error(path, line, f"unsupported inline Markdown token: {token.type}")
		index += 1
	return tuple(result)


#============================================
def parse_image(path: pathlib.Path, line: int, token: Token) -> marp_lib.native_model.Image:
	"""Convert one standalone image paragraph to a component image."""
	source = token.attrGet("src")
	if source is None:
		raise error(path, line, "image is missing a source")
	if source.startswith(("http://", "https://", "data:")):
		raise error(path, line, "component images must use a repository-relative source")
	if BACKGROUND_IMAGE_PATTERN.search(token.markup + token.content):
		raise error(path, line, "background-image modifiers are not supported")
	alt_text = token.content
	if not alt_text.strip():
		raise error(path, line, "component images require meaningful alt text")
	return marp_lib.native_model.Image(location(path, line), alt_text, source, token.attrGet("title"))


#============================================
def parse_list(path: pathlib.Path, tokens: list[Token], index: int, base_line: int) -> tuple[marp_lib.native_model.ListBlock, int]:
	"""Convert one markdown-it list span, retaining nesting and ordered starts."""
	opening = tokens[index]
	ordered = opening.type == "ordered_list_open"
	start_value = opening.attrGet("start")
	start = int(start_value) if start_value is not None else 1
	items: list[marp_lib.native_model.ListItem] = []
	index += 1
	while tokens[index].type != opening.type.replace("_open", "_close"):
		item_open = tokens[index]
		if item_open.type != "list_item_open":
			raise error(path, token_line(item_open, base_line), "list contains unsupported structure")
		item_line = token_line(item_open, base_line)
		index += 1
		inlines: tuple[marp_lib.native_model.Inline, ...] | None = None
		children: list[marp_lib.native_model.ListBlock] = []
		while tokens[index].type != "list_item_close":
			token = tokens[index]
			if token.type == "paragraph_open":
				if inlines is not None:
					raise error(path, token_line(token, base_line), "list items support one paragraph")
				inline = tokens[index + 1]
				if inline.type != "inline":
					raise error(path, token_line(token, base_line), "list item paragraph is malformed")
				inlines = parse_inlines(path, token_line(inline, base_line), inline.children or [])
				index += 3
			elif token.type in ("bullet_list_open", "ordered_list_open"):
				child, index = parse_list(path, tokens, index, base_line)
				children.append(child)
			else:
				raise error(path, token_line(token, base_line), "list contains unsupported structure")
		if inlines is None:
			raise error(path, item_line, "list item requires editable text")
		items.append(marp_lib.native_model.ListItem(location(path, item_line), inlines, tuple(children)))
		index += 1
	index += 1
	return marp_lib.native_model.ListBlock(location(path, token_line(opening, base_line)), ordered, start,
		tuple(items)), index


#============================================
def parse_blocks(path: pathlib.Path, tokens: list[Token], base_line: int,
		allow_cells: bool) -> tuple[tuple[marp_lib.native_model.Block, ...], tuple[marp_lib.native_model.Cell, ...]]:
	"""Convert supported block tokens and preserve top-level quote cells."""
	blocks: list[marp_lib.native_model.Block] = []
	cells: list[marp_lib.native_model.Cell] = []
	index = 0
	while index < len(tokens):
		token = tokens[index]
		line = token_line(token, base_line)
		if token.type == "heading_open":
			inline = tokens[index + 1]
			blocks.append(marp_lib.native_model.Heading(location(path, line), int(token.tag[1:]),
				parse_inlines(path, token_line(inline, base_line), inline.children or [])))
			index += 3
		elif token.type == "paragraph_open":
			inline = tokens[index + 1]
			children = inline.children or []
			images = [child for child in children if child.type == "image"]
			if images:
				if any(child.type != "image" and not (child.type == "text" and
					child.content.isspace()) for child in children):
					raise error(path, token_line(inline, base_line), "images cannot be mixed with inline text")
				for image in images:
					blocks.append(parse_image(path, token_line(inline, base_line), image))
			else:
				blocks.append(marp_lib.native_model.Paragraph(location(path, line),
					parse_inlines(path, token_line(inline, base_line), children)))
			index += 3
		elif token.type in ("bullet_list_open", "ordered_list_open"):
			list_block, index = parse_list(path, tokens, index, base_line)
			blocks.append(list_block)
		elif token.type == "blockquote_open" and allow_cells:
			end = index + 1
			depth = 1
			while end < len(tokens) and depth:
				if tokens[end].type == "blockquote_open":
					depth += 1
				elif tokens[end].type == "blockquote_close":
					depth -= 1
				end += 1
			if depth:
				raise error(path, line, "unclosed component cell")
			cell_blocks, nested_cells = parse_blocks(path, tokens[index + 1:end - 1], base_line, False)
			if nested_cells:
				raise error(path, line, "component cells cannot nest")
			cells.append(marp_lib.native_model.Cell(location(path, line), cell_blocks))
			index = end
		elif token.type in ("fence", "code_block", "table_open", "html_block", "html_inline"):
			raise error(path, line, f"unsupported Markdown block: {token.type}")
		else:
			raise error(path, line, f"unsupported Markdown token: {token.type}")
	return tuple(blocks), tuple(cells)


#============================================
def parse_deck(input_path: pathlib.Path) -> marp_lib.native_model.Deck:
	"""Parse one authoritative Marp Markdown file without Marp runtime code."""
	path = input_path.resolve()
	source = path.read_text(encoding="utf-8")
	front_matter, body, body_line = parse_front_matter(path, source)
	default_paginate = front_matter.get("paginate", True)
	parser = MarkdownIt("commonmark", {"breaks": True, "linkify": True}).enable("linkify").enable("table")
	parser.linkify.set({"fuzzy_link": False})
	slides: list[marp_lib.native_model.Slide] = []
	for raw_slide, slide_line in split_slides(path, body, body_line):
		if not raw_slide.strip():
			continue
		if re.fullmatch(r"\s*<!--\s*ODP hidden slide skipped:.*?-->\s*", raw_slide,
			re.DOTALL):
			continue
		cleaned, layout_class, paginate, notes = remove_comments(path, raw_slide, slide_line,
			default_paginate)
		if BACKGROUND_IMAGE_PATTERN.search(cleaned):
			raise error(path, slide_line, "background-image modifiers are not supported")
		blocks, cells = parse_blocks(path, parser.parse(cleaned), slide_line, True)
		slides.append(marp_lib.native_model.Slide(location(path, slide_line), layout_class, paginate,
			notes, blocks, cells))
	if not slides:
		raise error(path, body_line, "Marp Markdown contains no supported slides")
	repo_root = next((candidate for candidate in (path.parent, *path.parents)
		if (candidate / ".git").exists()), path.parent).resolve()
	return marp_lib.native_model.Deck(path, path.parent, repo_root, str(front_matter.get("title", "")),
		default_paginate, tuple(slides), front_matter)
