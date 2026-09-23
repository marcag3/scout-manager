import json
import os
from pathlib import Path

import frappe
from frappe import _

CONFIGS_ROOT = Path(__file__).resolve().parent / "configs" / "import"

PHP_TO_PYTHON_DATE = {
	"Y": "%Y",
	"m": "%m",
	"d": "%d",
	"H": "%H",
	"i": "%M",
	"s": "%S",
}

DELIMITERS = {
	"comma": ",",
	"semicolon": ";",
	"tab": "\t",
	"space": " ",
	"pipe": "|",
}


class ImportConfig:
	def __init__(self, data: dict):
		self.data = data
		self.roles = data.get("roles") or []
		self.role_indices = {role: idx for idx, role in enumerate(self.roles)}
		self.date_format = php_date_to_python(data.get("date") or "Y-m-d")
		self.delimiter = DELIMITERS.get(data.get("delimiter") or "comma", ",")
		self.has_headers = bool(data.get("headers"))
		self.conversion = bool(data.get("conversion"))
		self.ignore_duplicate_lines = bool(data.get("ignore_duplicate_lines"))
		self.encoding = data.get("encoding") or data.get("file_encoding")

	def get_column(self, role: str) -> int | None:
		return self.role_indices.get(role)

	@classmethod
	def from_path(cls, config_path: str) -> "ImportConfig":
		path = resolve_config_path(config_path)
		with open(path, encoding="utf-8") as handle:
			return cls(json.load(handle))

	@classmethod
	def from_file_url(cls, file_url: str) -> "ImportConfig":
		content = frappe.get_doc("File", {"file_url": file_url}).get_content()
		return cls(json.loads(content))


def list_bundled_configs() -> list[str]:
	configs: list[str] = []
	for path in sorted(CONFIGS_ROOT.rglob("*.json")):
		configs.append(str(path.relative_to(CONFIGS_ROOT)))
	return configs


def resolve_config_path(config_path: str) -> Path:
	path = Path(config_path)
	if path.is_absolute() and path.exists():
		return path

	candidate = CONFIGS_ROOT / config_path
	if candidate.exists():
		return candidate

	frappe.throw(_("Import config not found: {0}").format(config_path))


def php_date_to_python(php_format: str) -> str:
	result = []
	for char in php_format:
		if char in PHP_TO_PYTHON_DATE:
			result.append(PHP_TO_PYTHON_DATE[char])
		else:
			result.append(char)
	return "".join(result)


def get_default_config_path() -> str:
	return "ca/desjardins/account.json"
