import frappe 
from frappe import _
import client_demo.services.helper_functions as helpers

@frappe.whitelist(allow_guest=True)
def apply_leave(employee, leave_type, from_date, to_date, reason, half_day=None):
    # normalize input -> employee docname
    emp_docname = helpers.get_employee_docname(employee)
    if not emp_docname:
        return {"status": "error", "message": f"Employee not found: {employee}"}
     
    leave_approver = get_leave_approver(employee)

    # fetch company from employee doc
    company = frappe.db.get_value("Employee", emp_docname, "company")
    if not company:
        return {"status": "error", "message": "Employee has no Company set and no default available."}

    # optional: validate leave type
    if not frappe.db.exists("Leave Type", leave_type):
        return {"status": "error", "message": f"Leave Type not found: {leave_type}"}

    try:
        doc = frappe.new_doc("Leave Application")
        doc.employee = emp_docname               # <- use docname
        doc.employee_name = frappe.db.get_value("Employee", emp_docname, "employee_name")
        doc.leave_type = leave_type
        doc.from_date = from_date
        doc.to_date = to_date
        doc.company = company
        doc.description = reason
        doc.leave_approver = ""
        doc.half_day = 1 if half_day else 0
        doc.docstatus = 0

        doc.insert()
        frappe.db.commit()
        return {
            "status": "success",
            "message": f"Leave Application {doc.name} created. Pending approval from {leave_approver or 'HOD'}",
            "leave_name": doc.name
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error adding Leave Application")
        return {"status": "error", "message": str(e)}




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
        emp_docname = helpers.get_employee_docname(employee)
        if not emp_docname:
            return None
        return frappe.db.get_value("Employee", emp_docname, "reports_to")

        
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


@frappe.whitelist(allow_guest=True)
def approve_leave(leave_name, employee):
    # Input validation
    if not leave_name:
        return {"status": "error", "message": "leave_name is required"}
    if not employee:
        return {"status": "error", "message": "employee is required"}
    
    # Resolve employee correctly
    emp_docname = helpers.get_employee_docname(employee)
    if not emp_docname:
        return {"status": "error", "message": f"Employee not found: {employee}"}

    # Get manager info
    manager_name = frappe.db.get_value("Employee", emp_docname, "reports_to")

    try:
        # Load the Leave Application
        doc = frappe.get_doc("Leave Application", leave_name)

        # Check document state
        if doc.docstatus != 0:
            return {"status": "error", "message": "Leave Application already submitted"}

        # Approval text
        value = f"Approved by {manager_name if manager_name else 'HOD'}"
        prev_value = doc.custom_approved_by

        # Check if already approved
        if not prev_value:
            doc.set("custom_approved_by", value)
            doc.save(ignore_permissions=True)
            frappe.db.commit()
            return {"status": "success", "message": f"Leave approved: {value}"}
        else:
            return {"status": "error", "message": f"Leave already approved by {prev_value}"}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error approving leave")
        return {"status": "error", "message": str(e)}

 

