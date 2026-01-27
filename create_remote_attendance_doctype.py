# ============================================================
# REMOTE ATTENDANCE SYSTEM - BENCH CONSOLE SETUP SCRIPT
# ============================================================
# Run this in bench console:
#   cd ~/new_bench
#   bench --site <your-site> console
# Then paste the code below
# ============================================================

import frappe
from frappe.model.naming import make_autoname

# ============================================================
# STEP 1: CREATE REMOTE ATTENDANCE DOCTYPE
# ============================================================

print("Creating Remote Attendance DocType...")

# Check if already exists
if frappe.db.exists("DocType", "Remote Attendance"):
    print("DocType 'Remote Attendance' already exists. Deleting and recreating...")
    frappe.delete_doc("DocType", "Remote Attendance", force=True, ignore_permissions=True)
    frappe.db.commit()

# Create the DocType
doc = frappe.get_doc({
    "doctype": "DocType",
    "name": "Remote Attendance",
    "module": "Demo",
    "custom": 0,
    "is_submittable": 1,
    "istable": 0,
    "issingle": 0,
    "editable_grid": 1,
    "track_changes": 1,
    "naming_rule": "Expression",
    "autoname": "RA-.YYYY.-.#####",
    "sort_field": "modified",
    "sort_order": "DESC",
    "fields": [
        # Section: Employee Details
        {
            "fieldname": "employee",
            "fieldtype": "Link",
            "label": "Employee",
            "options": "Employee",
            "reqd": 1,
            "in_list_view": 1,
            "in_standard_filter": 1,
            "bold": 1
        },
        {
            "fieldname": "employee_name",
            "fieldtype": "Data",
            "label": "Employee Name",
            "fetch_from": "employee.employee_name",
            "read_only": 1,
            "in_list_view": 1
        },
        {
            "fieldname": "column_break_1",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "log_type",
            "fieldtype": "Select",
            "label": "Log Type",
            "options": "IN\nOUT",
            "reqd": 1,
            "in_list_view": 1,
            "in_standard_filter": 1,
            "bold": 1
        },
        {
            "fieldname": "time",
            "fieldtype": "Datetime",
            "label": "Time",
            "reqd": 1,
            "in_list_view": 1,
            "bold": 1
        },
        # Section: Location Details
        {
            "fieldname": "section_location",
            "fieldtype": "Section Break",
            "label": "Location Details"
        },
        {
            "fieldname": "location_type",
            "fieldtype": "Select",
            "label": "Location Type",
            "options": "\nWork From Home\nField\nService Center",
            "depends_on": "eval:doc.log_type=='IN'",
            "mandatory_depends_on": "eval:doc.log_type=='IN'",
            "in_list_view": 1,
            "in_standard_filter": 1
        },
        {
            "fieldname": "latitude",
            "fieldtype": "Float",
            "label": "Latitude",
            "precision": "8"
        },
        {
            "fieldname": "column_break_2",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "longitude",
            "fieldtype": "Float",
            "label": "Longitude",
            "precision": "8"
        },
        {
            "fieldname": "device_info",
            "fieldtype": "Data",
            "label": "Device Info"
        },
        # Section: Approval Details
        {
            "fieldname": "section_approval",
            "fieldtype": "Section Break",
            "label": "Approval Details"
        },
        {
            "fieldname": "workflow_state",
            "fieldtype": "Data",
            "label": "Workflow State",
            "read_only": 1,
            "in_list_view": 1,
            "in_standard_filter": 1
        },
        {
            "fieldname": "approved_by",
            "fieldtype": "Link",
            "label": "Approved By",
            "options": "Employee",
            "read_only": 1
        },
        {
            "fieldname": "column_break_3",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "approved_on",
            "fieldtype": "Datetime",
            "label": "Approved On",
            "read_only": 1
        },
        {
            "fieldname": "rejection_reason",
            "fieldtype": "Small Text",
            "label": "Rejection Reason",
            "read_only": 1,
            "depends_on": "eval:doc.workflow_state=='Rejected'"
        },
        # Section: Additional Info
        {
            "fieldname": "section_remarks",
            "fieldtype": "Section Break",
            "label": "Additional Information"
        },
        {
            "fieldname": "remarks",
            "fieldtype": "Small Text",
            "label": "Remarks"
        },
        {
            "fieldname": "column_break_4",
            "fieldtype": "Column Break"
        },
        {
            "fieldname": "linked_checkin",
            "fieldtype": "Link",
            "label": "Linked Employee Checkin",
            "options": "Employee Checkin",
            "read_only": 1,
            "description": "Created after approval"
        },
        # Amendment field for submittable
        {
            "fieldname": "amended_from",
            "fieldtype": "Link",
            "label": "Amended From",
            "options": "Remote Attendance",
            "read_only": 1,
            "no_copy": 1,
            "print_hide": 1
        }
    ],
    "permissions": [
        {
            "role": "System Manager",
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "submit": 1,
            "cancel": 1,
            "amend": 1
        },
        {
            "role": "HR Manager",
            "read": 1,
            "write": 1,
            "create": 1,
            "delete": 1,
            "submit": 1,
            "cancel": 1,
            "amend": 1
        },
        {
            "role": "HR User",
            "read": 1,
            "write": 1,
            "create": 1,
            "submit": 1
        },
        {
            "role": "Employee",
            "read": 1,
            "write": 1,
            "create": 1
        }
    ]
})

doc.insert(ignore_permissions=True)
frappe.db.commit()
print(f"✓ DocType 'Remote Attendance' created successfully!")

# ============================================================
# STEP 2: CREATE WORKFLOW
# ============================================================

print("\nCreating Remote Attendance Approval Workflow...")

# Check if workflow already exists
if frappe.db.exists("Workflow", "Remote Attendance Approval"):
    print("Workflow 'Remote Attendance Approval' already exists. Deleting and recreating...")
    frappe.delete_doc("Workflow", "Remote Attendance Approval", force=True, ignore_permissions=True)
    frappe.db.commit()

# Create the Workflow
workflow = frappe.get_doc({
    "doctype": "Workflow",
    "name": "Remote Attendance Approval",
    "workflow_name": "Remote Attendance Approval",
    "document_type": "Remote Attendance",
    "is_active": 1,
    "override_status": 0,
    "send_email_alert": 0,
    "workflow_state_field": "workflow_state",
    "states": [
        {
            "state": "Pending",
            "doc_status": "0",
            "is_optional_state": 0,
            "allow_edit": "Employee"
        },
        {
            "state": "Approved",
            "doc_status": "1",
            "is_optional_state": 0,
            "allow_edit": "HR Manager"
        },
        {
            "state": "Rejected",
            "doc_status": "0",
            "is_optional_state": 0,
            "allow_edit": "HR Manager"
        },
        {
            "state": "Cancelled",
            "doc_status": "0",
            "is_optional_state": 0,
            "allow_edit": "Employee"
        }
    ],
    "transitions": [
        {
            "state": "Pending",
            "action": "Approve",
            "next_state": "Approved",
            "allowed": "HR Manager",
            "allow_self_approval": 1
        },
        {
            "state": "Pending",
            "action": "Reject",
            "next_state": "Rejected",
            "allowed": "HR Manager",
            "allow_self_approval": 1
        },
        {
            "state": "Pending",
            "action": "Cancel",
            "next_state": "Cancelled",
            "allowed": "Employee",
            "allow_self_approval": 1
        }
    ]
})

workflow.insert(ignore_permissions=True)
frappe.db.commit()
print(f"✓ Workflow 'Remote Attendance Approval' created successfully!")

# ============================================================
# STEP 3: SYNC AND VERIFY
# ============================================================

print("\n" + "="*50)
print("SETUP COMPLETE!")
print("="*50)
print("\nCreated:")
print("  1. DocType: Remote Attendance")
print("  2. Workflow: Remote Attendance Approval")
print("\nWorkflow States:")
print("  - Pending (Draft)")
print("  - Approved (Submitted)")
print("  - Rejected (Draft)")
print("  - Cancelled (Cancelled)")
print("\nNext Steps:")
print("  1. Exit console: exit()")
print("  2. Run: bench --site <your-site> migrate")
print("  3. Clear cache: bench --site <your-site> clear-cache")
print("  4. Restart: bench restart")
print("="*50)
