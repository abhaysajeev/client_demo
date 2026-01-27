import frappe

@frappe.whitelist(allow_guest=True)
def get_employee_docname(employee_input):
    """
    Accepts:
    - Employee Docname (unique name field, e.g., 'AMAL R')

    Returns:
    - Employee docname (string)
    - or None if not found
    """

    # Validate that the employee exists by name
    if frappe.db.exists("Employee", employee_input):
        return employee_input

    return None
