import frappe 
from frappe import _


@frappe.whitelist(allow_guest=True)
def apply_leave(employee, leave_type, from_date, to_date, reason, half_day=None ):

    if not frappe.db.exists("Employee", employee):
        return {"Error": f"Employee not found: {employee}"}
    try:
        doc = frappe.new_doc("Leave Application")
        doc.employee = employee
        doc.leave_type = leave_type
        doc.from_date = from_date
        doc.to_date = to_date
        doc.description = reason
        doc.leave_approver = ""
        doc.half_day = 1 if half_day else 0
        doc.docstatus = 0

        try:
            leave_approver = get_leave_approver(employee)
        except Exception:
            leave_approver = None

        # from hrms.hr.doctype.leave_application.leave_application import LeaveApplication
        # LeaveApplication.validate_dates_across_allocation = lambda self: None    

        doc.insert()
        frappe.db.commit()
        return {"Success": f"Leave Application {doc.name} successfully submitted. Pending Approval from {leave_approver if leave_approver else 'HOD'}"}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error adding Leave Application")
        return {"Error": str(e) }



@frappe.whitelist(allow_guest=True)
def get_leave_types():
    try:
        leave_types = frappe.db.get_all("Leave Type", pluck= "name")
        return leave_types
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error fetching Leave Types")
        return {"error": str(e)}
    

@frappe.whitelist(allow_guest=True)
def get_leave_approver(employee):
    try:
        approver = frappe.db.get_value(
            "Employee",
            {"employee_name": employee},  
            "reports_to"                 
        )
        return approver
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error fetching Leave Approver")
        return {"error": str(e)}
    

@frappe.whitelist(allow_guest=True)
def get_hr_manager_user():
    """
    Returns the first active user with the role 'HR Manager'.
    """
    user = frappe.get_all(
        "Has Role",
        filters={"role": "HR Manager", "parenttype": "User"},
        fields=["parent"],
        limit_page_length=1
    )
    
    if user:
        return user  
    return None


@frappe.whitelist(allow_guest=True)
def get_unapproved_leaves(user_id):
    # get both manager id (Employee.name) and employee_name
    manager_id = frappe.db.get_value("Employee", {"user_id": user_id}, "name")
    manager_name = frappe.db.get_value("Employee", {"user_id": user_id}, "employee_name")

    if not manager_id and not manager_name:
        return {"status": "error", "message": f"No employee found for user  {user_id}"}

    # try to get reportees by reports_to = manager_id first (most common)
    reportees = frappe.get_all(
        "Employee",
        filters={"reports_to": manager_name },
        fields=["name", "employee_name", "user_id"]
    )

    if not reportees:
        return {
            "status": "success",
            "manager": manager_name,
            "reportees_count": 0,
            "leave_count": 0,
            "leaves": []
        }

    employee_ids = [r["name"] for r in reportees]

    leaves = frappe.get_all(
        "Leave Application",
        filters=[
            ["Leave Application", "employee", "in", employee_ids],
            ["Leave Application", "status", "=", "Open"],
            ["Leave Application", "docstatus", "=", 0]
        ],
        fields=[
            "name",
            "employee",
            "employee_name",
            "leave_type",
            "from_date",
            "to_date",
            "description",
            "status",
            "docstatus"
        ],
        order_by="from_date asc"
    )

    return {
        "status": "success",
        "manager": manager_name or manager_id,
        "reportees_count": len(reportees),
        "leave_count": len(leaves),
        "leaves": leaves
    }

@frappe.whitelist(allow_guest=True)
def approve_leaves(leave_names, manager):
    pass

# 
# @frappe.whitelist(allow_guest=True)  
# def approve_leaves(leave_names, manager_name=None):
#     """
#     leave_names: JSON string like '["LEAV-0001","LEAV-0002"]' or a single name.
#     manager: optional string to store in `approved_by`.
#     """
#     import json
#     try:
#         names = json.loads(leave_names) if isinstance(leave_names, str) and leave_names.strip().startswith("[") else [leave_names]
#     except Exception:
#         names = [leave_names]

#     results = []
#     for name in names:
#         try:
#             doc = frappe.get_doc("Leave Application", name)
#             value = f"Approved by {manager_name if manager_name else ''}"
#             frappe.db.set_value("Leave Application", name, "custom_approved_by", value, update_modified=True)
#             doc.save(ignore_permissions=True)  # use ignore_permissions only if appropriate
#             results.append({"name": name, "result": "ok"})
#         except Exception as e:
#             frappe.log_error(frappe.get_traceback(), "Error Approving Leave")
#             results.append({"name": name, "result": "error", "msg": str(e)})
#     return results


@frappe.whitelist(allow_guest=True)
def approve_leave(leave_name, employee):
    # Input validation
    if not leave_name:
        return {"status": "error", "message": "leave_name is required"}
    if not employee:
        return {"status": "error", "message": "employee is required"}
    
    # Get manager info
    manager_name = frappe.db.get_value("Employee", {"name": employee}, "reports_to")
    # Load document safely
    try:
        doc = frappe.get_doc("Leave Application", leave_name)
    except frappe.DoesNotExistError:
        return {"status": "error", "message": f"Leave Application {leave_name} not found"}
    
    # Check document state
    if doc.docstatus != 0:
        return {"status": "error", "message": "Leave Application already submitted"}
    
    # Update and save
    value = f"Approved by {manager_name if manager_name else 'HOD'}"
    try:
        doc.set("custom_approved_by", value)  
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        return {"status": "success", "message": f"Field updated on {leave_name}"}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error approving leave")
        return {"error": str(e)}
    
 

