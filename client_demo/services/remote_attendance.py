# File: client_demo/services/remote_attendance.py
# Remote Attendance APIs for Mobile App
# ============================================================

import frappe
from frappe import _
from frappe.utils import now_datetime, getdate, today, get_datetime
from datetime import datetime, timedelta
import client_demo.services.helper_functions as helpers


# ============================================================
# EMPLOYEE APIs (7 APIs)
# ============================================================

@frappe.whitelist(allow_guest=True)
def mark_remote_attendance(employee, latitude, longitude, location_type=None, device_info=None, remarks=None):
    """
    Mark remote attendance (IN/OUT) with GPS coordinates.
    
    Required: employee, latitude, longitude
    Required for IN: location_type (Work From Home / Field / Service Center)
    Optional: device_info, remarks
    """
    # Validate employee
    if not frappe.db.exists("Employee", employee):
        return {"success": False, "message": f"Employee {employee} not found"}
    
    # Get today's date
    today_date = getdate(today())
    current_time = now_datetime()
    
    # Determine log_type based on existing checkins today
    next_log_type = _get_next_log_type(employee, today_date)
    
    # Validate location_type for IN
    if next_log_type == "IN":
        valid_location_types = ["Work From Home", "Field", "Service Center"]
        if not location_type or location_type not in valid_location_types:
            return {
                "success": False, 
                "message": f"location_type is required for IN. Must be one of: {', '.join(valid_location_types)}"
            }
    
    # Get manager (reports_to) for approval message
    manager = frappe.db.get_value("Employee", employee, "reports_to")
    
    try:
        # Create Remote Attendance document
        doc = frappe.get_doc({
            "doctype": "Remote Attendance",
            "employee": employee,
            "log_type": next_log_type,
            "time": current_time,
            "latitude": float(latitude),
            "longitude": float(longitude),
            "location_type": location_type if next_log_type == "IN" else None,
            "device_info": device_info,
            "remarks": remarks,
            "workflow_state": "Pending"
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        
        return {
            "success": True,
            "name": doc.name,
            "log_type": next_log_type,
            "time": str(current_time),
            "location_type": location_type if next_log_type == "IN" else None,
            "workflow_state": "Pending",
            "message": f"Attendance marked as {next_log_type}. Pending approval from {manager or 'Manager'}"
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Remote Attendance Error")
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def get_today_attendance_status(employee):
    """
    Get today's attendance status for an employee.
    Returns next log type (IN/OUT) and current status.
    """
    if not frappe.db.exists("Employee", employee):
        return {"success": False, "message": f"Employee {employee} not found"}
    
    today_date = getdate(today())
    next_log_type = _get_next_log_type(employee, today_date)
    
    # Count today's checkins
    total_checkins = _count_today_checkins(employee, today_date)
    
    # Count pending approvals
    pending_count = frappe.db.count("Remote Attendance", {
        "employee": employee,
        "workflow_state": "Pending"
    })
    
    # Get last checkin
    last_checkin = _get_last_checkin(employee)
    
    return {
        "success": True,
        "date": str(today_date),
        "next_log_type": next_log_type,
        "total_checkins_today": total_checkins,
        "pending_approvals": pending_count,
        "last_checkin": last_checkin,
        "is_first_of_day": total_checkins == 0
    }


@frappe.whitelist(allow_guest=True)
def get_location_type_options():
    """
    Get available location type options for IN attendance.
    """
    return ["Work From Home", "Field", "Service Center"]


@frappe.whitelist(allow_guest=True)
def get_pending_remote_attendance(employee):
    """
    Get all pending remote attendance requests for an employee.
    """
    if not frappe.db.exists("Employee", employee):
        return {"success": False, "message": f"Employee {employee} not found"}
    
    pending = frappe.get_all(
        "Remote Attendance",
        filters={
            "employee": employee,
            "workflow_state": "Pending"
        },
        fields=["name", "log_type", "time", "location_type", "workflow_state", "latitude", "longitude", "remarks"],
        order_by="time desc"
    )
    
    return {
        "success": True,
        "count": len(pending),
        "data": pending
    }


@frappe.whitelist(allow_guest=True)
def get_remote_attendance_history(employee, from_date=None, to_date=None):
    """
    Get remote attendance history for an employee.
    Optional date filter.
    """
    if not frappe.db.exists("Employee", employee):
        return {"success": False, "message": f"Employee {employee} not found"}
    
    filters = {"employee": employee}
    
    # Apply date filters if provided
    if from_date and to_date:
        filters["time"] = ["between", [from_date, to_date + " 23:59:59"]]
    elif from_date:
        filters["time"] = [">=", from_date]
    elif to_date:
        filters["time"] = ["<=", to_date + " 23:59:59"]
    
    records = frappe.get_all(
        "Remote Attendance",
        filters=filters,
        fields=[
            "name", "log_type", "time", "location_type", 
            "workflow_state", "approved_by", "approved_on",
            "rejection_reason", "linked_checkin", "latitude", "longitude"
        ],
        order_by="time desc"
    )
    
    return {
        "success": True,
        "count": len(records),
        "data": records
    }


@frappe.whitelist(allow_guest=True)
def cancel_remote_attendance(name, employee):
    """
    Cancel a pending remote attendance request.
    Only the employee who created it can cancel, and only if Pending.
    """
    if not frappe.db.exists("Remote Attendance", name):
        return {"success": False, "message": f"Remote Attendance {name} not found"}
    
    # Set ignore permissions for guest access
    frappe.flags.ignore_permissions = True
    
    doc = frappe.get_doc("Remote Attendance", name)
    
    # Validate ownership
    if doc.employee != employee:
        return {"success": False, "message": "You can only cancel your own attendance requests"}
    
    # Validate status
    if doc.workflow_state != "Pending":
        return {"success": False, "message": f"Cannot cancel. Current status is {doc.workflow_state}"}
    
    try:
        # Use db_set to bypass workflow state machine validation
        frappe.db.set_value("Remote Attendance", name, "workflow_state", "Cancelled")
        frappe.db.commit()
        
        return {
            "success": True,
            "message": f"Remote Attendance {name} cancelled successfully"
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Cancel Remote Attendance Error")
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def get_today_checkin_pairs(employee):
    """
    Get today's IN/OUT pairs with duration for an employee.
    Combines both Remote Attendance (approved) and Employee Checkin.
    """
    if not frappe.db.exists("Employee", employee):
        return {"success": False, "message": f"Employee {employee} not found"}
    
    today_date = getdate(today())
    today_start = f"{today_date} 00:00:00"
    today_end = f"{today_date} 23:59:59"
    
    # Get approved Remote Attendance
    remote_checkins = frappe.get_all(
        "Remote Attendance",
        filters={
            "employee": employee,
            "workflow_state": "Approved",
            "time": ["between", [today_start, today_end]]
        },
        fields=["log_type", "time", "location_type"],
        order_by="time asc"
    )
    
    # Get Employee Checkins (from biometric/other sources)
    employee_checkins = frappe.get_all(
        "Employee Checkin",
        filters={
            "employee": employee,
            "time": ["between", [today_start, today_end]]
        },
        fields=["log_type", "time"],
        order_by="time asc"
    )
    
    # Combine and sort all checkins
    all_checkins = []
    for r in remote_checkins:
        all_checkins.append({
            "log_type": r.log_type,
            "time": r.time,
            "location_type": r.location_type,
            "source": "remote"
        })
    for e in employee_checkins:
        all_checkins.append({
            "log_type": e.log_type,
            "time": e.time,
            "location_type": None,
            "source": "biometric"
        })
    
    all_checkins.sort(key=lambda x: x["time"])
    
    # Build pairs
    pairs = []
    total_hours = 0.0
    i = 0
    
    while i < len(all_checkins):
        if all_checkins[i]["log_type"] == "IN":
            in_time = all_checkins[i]["time"]
            location_type = all_checkins[i].get("location_type")
            source = all_checkins[i]["source"]
            out_time = None
            duration = None
            
            # Look for matching OUT
            if i + 1 < len(all_checkins) and all_checkins[i + 1]["log_type"] == "OUT":
                out_time = all_checkins[i + 1]["time"]
                duration = round((out_time - in_time).total_seconds() / 3600, 2)
                total_hours += duration
                i += 2
            else:
                i += 1
            
            pairs.append({
                "in_time": in_time.strftime("%H:%M") if in_time else None,
                "out_time": out_time.strftime("%H:%M") if out_time else None,
                "location_type": location_type,
                "duration_hours": duration,
                "source": source
            })
        else:
            i += 1
    
    return {
        "success": True,
        "date": str(today_date),
        "pairs": pairs,
        "total_hours": round(total_hours, 2)
    }


# ============================================================
# MANAGER APIs (4 APIs)
# ============================================================

@frappe.whitelist(allow_guest=True)
def get_pending_approvals(user_id):
    """
    Get all pending remote attendance requests for manager's reportees.
    """
    # Get manager's employee ID
    manager_id = frappe.db.get_value("Employee", {"user_id": user_id}, "name")
    
    if not manager_id:
        return {"success": False, "message": f"No employee found for user {user_id}"}
    
    # Get all reportees
    reportees = frappe.get_all(
        "Employee",
        filters={"reports_to": manager_id, "status": "Active"},
        fields=["name", "employee_name"]
    )
    
    if not reportees:
        return {
            "success": True,
            "manager": manager_id,
            "reportees_count": 0,
            "pending_count": 0,
            "data": []
        }
    
    reportee_ids = [r["name"] for r in reportees]
    
    # Get pending requests
    pending = frappe.get_all(
        "Remote Attendance",
        filters={
            "employee": ["in", reportee_ids],
            "workflow_state": "Pending"
        },
        fields=[
            "name", "employee", "employee_name", "log_type", "time",
            "location_type", "latitude", "longitude", "remarks", "device_info"
        ],
        order_by="time asc"
    )
    
    return {
        "success": True,
        "manager": manager_id,
        "reportees_count": len(reportees),
        "pending_count": len(pending),
        "data": pending
    }


@frappe.whitelist(allow_guest=True)
def approve_remote_attendance(name, manager):
    """
    Approve a remote attendance request.
    Creates actual Employee Checkin record and submits the document.
    """
    if not frappe.db.exists("Remote Attendance", name):
        return {"success": False, "message": f"Remote Attendance {name} not found"}
    
    if not frappe.db.exists("Employee", manager):
        return {"success": False, "message": f"Manager {manager} not found"}
    
    # Set ignore permissions for guest access
    frappe.flags.ignore_permissions = True
    
    doc = frappe.get_doc("Remote Attendance", name)
    
    # Validate the request is pending
    if doc.workflow_state != "Pending":
        return {"success": False, "message": f"Cannot approve. Current status is {doc.workflow_state}"}
    
    # Validate manager has authority
    employee_manager = frappe.db.get_value("Employee", doc.employee, "reports_to")
    if employee_manager != manager:
        return {"success": False, "message": f"You are not authorized to approve this request. Expected manager: {employee_manager}"}
    
    try:
        current_time = now_datetime()
        
        # Create actual Employee Checkin record
        checkin = frappe.get_doc({
            "doctype": "Employee Checkin",
            "employee": doc.employee,
            "log_type": doc.log_type,
            "time": doc.time,
            "device_id": f"Remote-{doc.location_type or 'Mobile'}",
            "shift": frappe.db.get_value("Employee", doc.employee, "default_shift")
        })
        checkin.insert(ignore_permissions=True)
        
        # Use db_set to bypass workflow state machine validation
        frappe.db.set_value("Remote Attendance", name, {
            "workflow_state": "Approved",
            "approved_by": manager,
            "approved_on": current_time,
            "linked_checkin": checkin.name,
            "docstatus": 1
        })
        
        frappe.db.commit()
        
        return {
            "success": True,
            "message": "Approved and checkin created",
            "remote_attendance": doc.name,
            "employee_checkin": checkin.name
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Approve Remote Attendance Error")
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def reject_remote_attendance(name, manager, reason):
    """
    Reject a remote attendance request with mandatory reason.
    """
    if not frappe.db.exists("Remote Attendance", name):
        return {"success": False, "message": f"Remote Attendance {name} not found"}
    
    if not frappe.db.exists("Employee", manager):
        return {"success": False, "message": f"Manager {manager} not found"}
    
    if not reason or not reason.strip():
        return {"success": False, "message": "Rejection reason is mandatory"}
    
    # Set ignore permissions for guest access
    frappe.flags.ignore_permissions = True
    
    doc = frappe.get_doc("Remote Attendance", name)
    
    # Validate the request is pending
    if doc.workflow_state != "Pending":
        return {"success": False, "message": f"Cannot reject. Current status is {doc.workflow_state}"}
    
    # Validate manager has authority
    employee_manager = frappe.db.get_value("Employee", doc.employee, "reports_to")
    if employee_manager != manager:
        return {"success": False, "message": f"You are not authorized to reject this request. Expected manager: {employee_manager}"}
    
    try:
        # Use db_set to bypass workflow state machine validation
        frappe.db.set_value("Remote Attendance", name, {
            "workflow_state": "Rejected",
            "approved_by": manager,
            "approved_on": now_datetime(),
            "rejection_reason": reason.strip()
        })
        
        frappe.db.commit()
        
        return {
            "success": True,
            "message": f"Remote Attendance {name} rejected",
            "reason": reason.strip()
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Reject Remote Attendance Error")
        return {"success": False, "message": str(e)}


@frappe.whitelist(allow_guest=True)
def get_approval_history(user_id, from_date=None, to_date=None):
    """
    Get manager's approval/rejection history with optional date filter.
    """
    # Get manager's employee ID
    manager_id = frappe.db.get_value("Employee", {"user_id": user_id}, "name")
    
    if not manager_id:
        return {"success": False, "message": f"No employee found for user {user_id}"}
    
    filters = {
        "approved_by": manager_id,
        "workflow_state": ["in", ["Approved", "Rejected"]]
    }
    
    # Apply date filters
    if from_date and to_date:
        filters["approved_on"] = ["between", [from_date, to_date + " 23:59:59"]]
    elif from_date:
        filters["approved_on"] = [">=", from_date]
    elif to_date:
        filters["approved_on"] = ["<=", to_date + " 23:59:59"]
    
    records = frappe.get_all(
        "Remote Attendance",
        filters=filters,
        fields=[
            "name", "employee", "employee_name", "log_type", "time",
            "location_type", "workflow_state", "approved_on", "rejection_reason"
        ],
        order_by="approved_on desc"
    )
    
    # Count approved and rejected
    approved_count = len([r for r in records if r.workflow_state == "Approved"])
    rejected_count = len([r for r in records if r.workflow_state == "Rejected"])
    
    return {
        "success": True,
        "manager": manager_id,
        "count": len(records),
        "approved": approved_count,
        "rejected": rejected_count,
        "data": records
    }


# ============================================================
# HELPER FUNCTIONS (Private)
# ============================================================

def _get_next_log_type(employee, target_date):
    """
    Determine next log type (IN/OUT) based on existing checkins today.
    Checks both Remote Attendance (approved) and Employee Checkin.
    """
    today_start = f"{target_date} 00:00:00"
    today_end = f"{target_date} 23:59:59"
    
    # Get last approved Remote Attendance today
    last_remote = frappe.db.get_value(
        "Remote Attendance",
        filters={
            "employee": employee,
            "workflow_state": "Approved",
            "time": ["between", [today_start, today_end]]
        },
        fieldname="log_type",
        order_by="time desc"
    )
    
    # Get last Employee Checkin today
    last_checkin = frappe.db.get_value(
        "Employee Checkin",
        filters={
            "employee": employee,
            "time": ["between", [today_start, today_end]]
        },
        fieldname="log_type",
        order_by="time desc"
    )
    
    # Also check pending Remote Attendance (treat as if already logged)
    last_pending = frappe.db.get_value(
        "Remote Attendance",
        filters={
            "employee": employee,
            "workflow_state": "Pending",
            "time": ["between", [today_start, today_end]]
        },
        fieldname="log_type",
        order_by="time desc"
    )
    
    # Get the most recent log_type from all sources
    # For simplicity, if any pending exists, use that as reference
    if last_pending:
        return "OUT" if last_pending == "IN" else "IN"
    
    # Otherwise check approved/actual checkins
    if last_remote or last_checkin:
        # Determine which is more recent
        last_log = last_remote or last_checkin
        return "OUT" if last_log == "IN" else "IN"
    
    # No checkins today, first should be IN
    return "IN"


def _count_today_checkins(employee, target_date):
    """
    Count total checkins today (approved Remote + Employee Checkin).
    """
    today_start = f"{target_date} 00:00:00"
    today_end = f"{target_date} 23:59:59"
    
    remote_count = frappe.db.count(
        "Remote Attendance",
        filters={
            "employee": employee,
            "workflow_state": "Approved",
            "time": ["between", [today_start, today_end]]
        }
    )
    
    checkin_count = frappe.db.count(
        "Employee Checkin",
        filters={
            "employee": employee,
            "time": ["between", [today_start, today_end]]
        }
    )
    
    pending_count = frappe.db.count(
        "Remote Attendance",
        filters={
            "employee": employee,
            "workflow_state": "Pending",
            "time": ["between", [today_start, today_end]]
        }
    )
    
    return remote_count + checkin_count + pending_count


def _get_last_checkin(employee):
    """
    Get the most recent checkin for an employee.
    """
    # Check Remote Attendance first
    last_remote = frappe.get_all(
        "Remote Attendance",
        filters={
            "employee": employee,
            "workflow_state": ["in", ["Pending", "Approved"]]
        },
        fields=["name", "log_type", "time", "workflow_state", "location_type"],
        order_by="time desc",
        limit=1
    )
    
    # Check Employee Checkin
    last_checkin = frappe.get_all(
        "Employee Checkin",
        filters={"employee": employee},
        fields=["name", "log_type", "time"],
        order_by="time desc",
        limit=1
    )
    
    if not last_remote and not last_checkin:
        return None
    
    if last_remote and last_checkin:
        if last_remote[0].time > last_checkin[0].time:
            return {
                "name": last_remote[0].name,
                "log_type": last_remote[0].log_type,
                "time": str(last_remote[0].time),
                "status": last_remote[0].workflow_state,
                "source": "remote"
            }
        else:
            return {
                "name": last_checkin[0].name,
                "log_type": last_checkin[0].log_type,
                "time": str(last_checkin[0].time),
                "status": "Approved",
                "source": "biometric"
            }
    
    if last_remote:
        return {
            "name": last_remote[0].name,
            "log_type": last_remote[0].log_type,
            "time": str(last_remote[0].time),
            "status": last_remote[0].workflow_state,
            "source": "remote"
        }
    
    return {
        "name": last_checkin[0].name,
        "log_type": last_checkin[0].log_type,
        "time": str(last_checkin[0].time),
        "status": "Approved",
        "source": "biometric"
    }
