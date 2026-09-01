"""Typed, presentation-neutral semantic objects for canonical Marp Markdown."""

# Standard Library
import enum
import pathlib
from dataclasses import dataclass, field


@dataclass(frozen=True)
class SourceLocation:
	"""One physical source position retained through native rendering."""
	path: pathlib.Path
	line: int


class FontSizePreset(enum.IntEnum):
	"""Supported explicit H1 display sizes in canonical CSS pixels."""
	SIZE_64 = 64
	SIZE_80 = 80
	SIZE_96 = 96
	SIZE_120 = 120
	SIZE_160 = 160
	SIZE_200 = 200


@dataclass(frozen=True)
class TitleSizeOverride:
	"""One source-located H1 display-size request."""
	location: SourceLocation
	preset: FontSizePreset


@dataclass(frozen=True)
class Text:
	"""Visible editable text."""
	value: str


@dataclass(frozen=True)
class Strong:
	"""Strong inline content."""
	children: tuple["Inline", ...]


@dataclass(frozen=True)
class Emphasis:
	"""Emphasized inline content."""
	children: tuple["Inline", ...]


@dataclass(frozen=True)
class InlineCode:
	"""Editable inline code content."""
	value: str


@dataclass(frozen=True)
class Link:
	"""Editable external hyperlink content."""
	children: tuple["Inline", ...]
	url: str


@dataclass(frozen=True)
class Break:
	"""An author-requested editable line break."""


Inline = Text | Strong | Emphasis | InlineCode | Link | Break


@dataclass(frozen=True)
class Heading:
	"""A semantic heading block."""
	location: SourceLocation
	level: int
	inlines: tuple[Inline, ...]


@dataclass(frozen=True)
class Paragraph:
	"""A semantic editable paragraph."""
	location: SourceLocation
	inlines: tuple[Inline, ...]


@dataclass(frozen=True)
class Image:
	"""One ordinary component image with its author-provided description."""
	location: SourceLocation
	alt_text: str
	source: str
	title: str | None


@dataclass(frozen=True)
class ListItem:
	"""One list item and its nested semantic lists."""
	location: SourceLocation
	inlines: tuple[Inline, ...]
	children: tuple["ListBlock", ...] = ()


@dataclass(frozen=True)
class ListBlock:
	"""An ordered or unordered semantic list."""
	location: SourceLocation
	ordered: bool
	start: int
	items: tuple[ListItem, ...]


Block = Heading | Paragraph | Image | ListBlock


@dataclass(frozen=True)
class Cell:
	"""One top-level blockquote component cell in source reading order."""
	location: SourceLocation
	blocks: tuple[Block, ...]


@dataclass(frozen=True)
class Slide:
	"""One canonical source slide, ready for a named native layout builder."""
	location: SourceLocation
	layout_class: str
	title_size_override: TitleSizeOverride | None
	paginate: bool
	notes: tuple[str, ...]
	blocks: tuple[Block, ...]
	cells: tuple[Cell, ...]


@dataclass(frozen=True)
class Deck:
	"""A parsed canonical deck and its authoritative source metadata."""
	path: pathlib.Path
	asset_root: pathlib.Path
	repo_root: pathlib.Path
	title: str
	paginate: bool
	slides: tuple[Slide, ...]
	front_matter: dict[str, object] = field(compare=False)
