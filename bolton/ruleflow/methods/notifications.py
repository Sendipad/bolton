# Copyright (c) 2025, Bolton and contributors
# For license information, please see license.txt

"""
Notification process methods for the Bolton Rule Engine
"""

import frappe
from frappe import _


def send_email_notification(doc, context, recipients, subject, message, attach_document=False, **kwargs):
	"""
	Send email notification
	
	Args:
		doc: Document being processed
		context: Execution context
		recipients: List of email addresses or comma-separated string
		subject: Email subject
		message: Email message (can include Jinja template variables)
		attach_document: Whether to attach the document as PDF
		
	Returns:
		Number of emails sent
	"""
	# Parse recipients
	if isinstance(recipients, str):
		recipients = [r.strip() for r in recipients.split(',')]
	
	# Render message template
	from frappe.utils.jinja import render_template
	rendered_message = render_template(message, {'doc': doc, 'frappe': frappe})
	rendered_subject = render_template(subject, {'doc': doc, 'frappe': frappe})
	
	# Prepare attachments
	attachments = []
	if attach_document and hasattr(doc, 'name'):
		try:
			pdf = frappe.get_print(doc.doctype, doc.name, print_format="Standard", as_pdf=True)
			attachments.append({
				'fname': f"{doc.name}.pdf",
				'fcontent': pdf
			})
		except Exception as e:
			frappe.logger().warning(f"Could not attach document PDF: {str(e)}")
	
	# Send email
	try:
		frappe.sendmail(
			recipients=recipients,
			subject=rendered_subject,
			message=rendered_message,
			attachments=attachments
		)
		return len(recipients)
	except Exception as e:
		frappe.log_error(f"Email notification failed: {str(e)}")
		raise


def create_todo(doc, context, assigned_to, description, priority="Medium", **kwargs):
	"""
	Create a TODO task
	
	Args:
		doc: Document being processed
		context: Execution context
		assigned_to: User to assign the TODO to
		description: TODO description
		priority: Priority level (Low, Medium, High)
		
	Returns:
		Name of created TODO
	"""
	todo = frappe.get_doc({
		'doctype': 'ToDo',
		'allocated_to': assigned_to,
		'description': description,
		'priority': priority,
		'reference_type': doc.doctype,
		'reference_name': doc.name,
		'status': 'Open'
	})
	
	todo.insert(ignore_permissions=True)
	return todo.name


def create_notification_log(doc, context, for_user, subject, message, type="Alert", **kwargs):
	"""
	Create a notification log entry
	
	Args:
		doc: Document being processed
		context: Execution context
		for_user: User to notify
		subject: Notification subject
		message: Notification message
		type: Notification type (Alert, Share, Assignment, etc.)
		
	Returns:
		Name of created Notification Log
	"""
	notification = frappe.get_doc({
		'doctype': 'Notification Log',
		'for_user': for_user,
		'subject': subject,
		'email_content': message,
		'type': type,
		'document_type': doc.doctype,
		'document_name': doc.name
	})
	
	notification.insert(ignore_permissions=True)
	return notification.name


def send_sms(doc, context, phone_numbers, message, **kwargs):
	"""
	Send SMS notification
	
	Args:
		doc: Document being processed
		context: Execution context
		phone_numbers: List of phone numbers or comma-separated string
		message: SMS message
		
	Returns:
		Number of SMS sent
	"""
	# Parse phone numbers
	if isinstance(phone_numbers, str):
		phone_numbers = [p.strip() for p in phone_numbers.split(',')]
	
	# Render message template
	from frappe.utils.jinja import render_template
	rendered_message = render_template(message, {'doc': doc, 'frappe': frappe})
	
	# Send SMS using Frappe's SMS integration
	try:
		for number in phone_numbers:
			frappe.sendmail(
				recipients=[number],
				message=rendered_message,
				is_sms=True
			)
		return len(phone_numbers)
	except Exception as e:
		frappe.log_error(f"SMS notification failed: {str(e)}")
		raise


def create_comment(doc, context, comment_text, comment_type="Comment", **kwargs):
	"""
	Create a comment on the document
	
	Args:
		doc: Document being processed
		context: Execution context
		comment_text: Comment content
		comment_type: Type of comment (Comment, Info, etc.)
		
	Returns:
		Name of created Comment
	"""
	comment = frappe.get_doc({
		'doctype': 'Comment',
		'comment_type': comment_type,
		'reference_doctype': doc.doctype,
		'reference_name': doc.name,
		'content': comment_text
	})
	
	comment.insert(ignore_permissions=True)
	return comment.name


def post_to_slack(doc, context, webhook_url, message, **kwargs):
	"""
	Post message to Slack webhook
	
	Args:
		doc: Document being processed
		context: Execution context
		webhook_url: Slack webhook URL
		message: Message to post (can include Jinja template)
		
	Returns:
		Boolean: True if successful
	"""
	import requests
	from frappe.utils.jinja import render_template
	
	# Render message
	rendered_message = render_template(message, {'doc': doc, 'frappe': frappe})
	
	# Post to Slack
	try:
		response = requests.post(
			webhook_url,
			json={'text': rendered_message},
			timeout=10
		)
		response.raise_for_status()
		return True
	except Exception as e:
		frappe.logger().error(f"Slack notification failed: {str(e)}")
		return False
