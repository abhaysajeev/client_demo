# File: your_app/your_app/api/attendance.py
import frappe
from frappe import _
import datetime 
@frappe.whitelist(allow_guest=True)
def mark_attendance(employee=None, log_type=None, device_id=None, shift=None):
    """
    Insert an attendance record into Employee Checkin.
    Required: employee, log_type, time
    Optional: device_id, shift

    """

    employee = "Arun R"
    # Validate employee exists
    if not frappe.db.exists("Employee", employee):
        return {"success": False, "message": _(f"Employee {employee} not found")}

    # # Validate log_type
    # if log_type not in ["IN", "OUT"]:
    #     return {"success": False, "message": _("Invalid log_type, must be IN or OUT")}

    # Create Employee Checkin record

    time = datetime.datetime.now()

    try:
        checkin = frappe.get_doc({
            "doctype": "Employee Checkin",
            "employee": employee,
            "log_type": log_type,
            "time": time,
            "device_id": device_id,
            "shift": shift
        })
        checkin.insert(ignore_permissions=True)  # allow guest insert
        frappe.db.commit()
        return {"success": True, "message": "Attendance recorded successfully"}
    except Exception as e:
        return {"success": False, "message": str(e)}

