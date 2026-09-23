"""Restore workspace widget lookup key after English asset rename."""

from scout_manager.scout_manager.setup.treasurer import refresh_renamed_workspace_links


def execute():
	refresh_renamed_workspace_links()
