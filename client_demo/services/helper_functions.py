import frappe

def get_employee_docname(employee_input):
    """
    Accepts:
    - Employee Docname (EMP-0001)
    - Employee Name (employee_name)

    Returns:
    - Employee docname (string)
    - or None if not found
    """

    # Case 1: Direct docname match
    if frappe.db.exists("Employee", employee_input):
        return employee_input

    # Case 2: Match via employee_name field
    docname = frappe.db.get_value("Employee", {"employee_name": employee_input}, "name")
    if docname:
        return docname

    return "No Employee Data Found for the given Employee"
