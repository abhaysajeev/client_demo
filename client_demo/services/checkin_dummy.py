# File: your_app/your_app/api/attendance.py
import frappe
from frappe import _
import datetime 


@frappe.whitelist(allow_guest=True)
def mark_attendance(employee, log_type=None, device_id=None, shift=None):
    """
    Insert an attendance record into Employee Checkin.
    If log_type is not provided, determine it based on the last checkin.
    Required: employee
    Optional: log_type, device_id, shift
    """

    # Validate employee exists
    if not frappe.db.exists("Employee", employee):
        return {"success": False, "message": _(f"Employee {employee} not found")}

    try:
        # If log_type not passed, decide automatically
        if not log_type:
            last_log = frappe.db.get_value(
                "Employee Checkin",
                {"employee": employee},
                ["log_type"],
                order_by="time desc"
            )

            if last_log == "IN":
                log_type = "OUT"
            else:
                log_type = "IN"

        # Current timestamp
        time = datetime.datetime.now()

        # Create Employee Checkin record
        checkin = frappe.get_doc({
            "doctype": "Employee Checkin",
            "employee": employee,
            "log_type": log_type,
            "time": time,
            "device_id": device_id,
            "shift": shift
        })
        checkin.insert(ignore_permissions=True)
        frappe.db.commit()

        return {
            "success": True,
            "message": f"Attendance recorded successfully as {log_type}",
            "log_type": log_type,
            "time": time
        }

    except Exception as e:
        return {"success": False, "message": str(e)}
    


@frappe.whitelist(allow_guest=True)
def get_employee_details(user_id):
    """
    Fetch employee details by linked user_id.
    Returns name, department, designation, team etc.
    """

    # Check if user exists
    if not frappe.db.exists("User", user_id):
        return {"success": False, "message": _(f"User {user_id} not found")}

    # Find employee linked to this user
    employee = frappe.db.get_value(
        "Employee",
        {"user_id": user_id},
        ["name", "employee_name", "department", "designation"],
        as_dict=True
    )

    if not employee:
        return {"success": False, "message": _(f"No Employee linked with user {user_id}")}

    return {
        "success": True,
        "data": employee
    }

import datetime

@frappe.whitelist(allow_guest=True)
def get_employee_checkins(employee, from_date, to_date):
    """
    Fetch check-in records for an employee between from_date and to_date.
    Dates should be in YYYY-MM-DD format. Inclusive of both dates.
    """

    if not frappe.db.exists("Employee", employee):
        return {"success": False, "message": _(f"Employee {employee} not found")}

    try:
        from_dt = datetime.datetime.strptime(from_date, "%Y-%m-%d")
        # set to_date as end of day 23:59:59
        to_dt = datetime.datetime.strptime(to_date, "%Y-%m-%d") + datetime.timedelta(days=1) - datetime.timedelta(seconds=1)

        checkins = frappe.get_all(
            "Employee Checkin",
            filters={
                "employee": employee,
                "time": ["between", [from_dt, to_dt]]
            },
            fields=["name", "time", "log_type"],
            order_by="time asc"
        )

        return {
            "success": True,
            "count": len(checkins),
            "data": checkins
        }

    except Exception as e:
        return {"success": False, "message": str(e)}
