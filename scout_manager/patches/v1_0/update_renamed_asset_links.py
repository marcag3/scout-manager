"""Refresh workspace links after French asset names were renamed."""

from scout_manager.scout_manager.setup.treasurer import refresh_renamed_workspace_links


def execute():
	refresh_renamed_workspace_links()
