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

import frappe

@frappe.whitelist()
def get_unapproved_leaves(user_id):
    """
    Return open, draft (docstatus=0) Leave Applications for employees who report to
    the employee corresponding to the given user_id.

    Response format (example):
    {
        "status": "success",
        "manager": "John Manager",
        "reportees_count": 2,
        "leave_count": 3,
        "leaves": [
            {
                "name": "LEAVE-0001",
                "employee": "EMP/0005",
                "employee_name": "Alice Employee",
                "leave_type": "Casual Leave",
                "from_date": "2025-10-01",
                "to_date": "2025-10-02",
                "description": "Family Event",
                "status": "Open",
                "docstatus": 0
            }, ...
        ]
    }
    """

    # 1) Get manager's employee_name from user_id
    manager_name = frappe.db.get_value("Employee", {"user_id": user_id}, "employee_name")
    if not manager_name:
        return {"status": "error", "message": f"No employee found for user_id {user_id}"}

    # 2) Get direct reportees (Employee.name is the employee ID, e.g. "EMP/0001")
    reportees = frappe.get_all(
        "Employee",
        filters={"reports_to": manager_name},
        fields=["name", "employee_name", "user_id"]
    )

    employee_names = [r["employee_name"] for r in reportees]

    # 3) Query Leave Applications where employee in reportees, status = "Open" and docstatus = 0
    leaves = frappe.get_all(
        "Leave Application",
        filters=[
            ["Leave Application", "employee", "in", employee_names],
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
        "manager": manager_name,
        "reportees_count": len(reportees),
        "leave_count": len(leaves),
        "leaves": leaves
    }



