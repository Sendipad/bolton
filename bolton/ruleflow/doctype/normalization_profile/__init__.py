# Copyright (c) 2025, Bolton and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class NormalizationProfile(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		description: DF.SmallText | None
		is_active: DF.Check
		normalize_fields_json: DF.Code | None
		profile_name: DF.Data
		target_doctype: DF.Link | None
	# end: auto-generated types

	pass
