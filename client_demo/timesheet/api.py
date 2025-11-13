import frappe
from frappe import _


@frappe.whitelist(allow_guest=True)
def get_timesheets_with_logs(start_date):
    timesheets = frappe.get_all("Timesheet",
        filters={"start_date": start_date},
        fields=["name", "employee", "employee_name", "status", "total_hours", "start_date", "end_date"]
    )
    for ts in timesheets:
        ts["time_logs"] = frappe.get_all("Timesheet Detail",
            filters={"parent": ts["name"]},
            fields=["activity_type", "project", "hours", "task", "from_time", "to_time", "description"]
        )
    return timesheets
