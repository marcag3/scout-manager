"""Seed the default Desjardins import config and migrate Scout Bank Import links."""

import frappe

from scout_manager.scout_manager.bank_reconciliation.default_configs import (
	migrate_scout_bank_import_configs,
	sync_desjardins_default_config,
)


def execute():
	config_name = sync_desjardins_default_config()
	migrate_scout_bank_import_configs(config_name)
