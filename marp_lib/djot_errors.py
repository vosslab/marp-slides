"""Source-located errors shared by the repository-owned Djot parser layers."""

# Local Modules
import marp_lib.native_model


class DjotParseError(ValueError):
	"""Report an actionable extended-Djot source parsing failure."""


#============================================
def source_error(location: marp_lib.native_model.SourceLocation, message: str) -> DjotParseError:
	"""Create one uniformly source-located Djot parsing error."""
	error_message = f"{location.path}:{location.line}: {message}"
	return DjotParseError(error_message)
