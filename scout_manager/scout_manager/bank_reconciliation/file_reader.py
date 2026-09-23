import frappe


def read_import_file_bytes(file_url: str) -> bytes:
	"""Read the raw CSV bytes without Frappe's UTF-8-first decoding."""
	file_doc = frappe.get_doc("File", {"file_url": file_url})
	if file_doc.get("content") and not file_doc.exists_on_disk():
		content = file_doc.content
		if isinstance(content, str):
			return content.encode("utf-8")
		return content

	file_doc.validate_file_path()
	with open(file_doc.get_full_path(), "rb") as handle:
		return handle.read()
