from app.table_models.table_employee import Employee


def build_employee_tools(employee: Employee) -> Employee:
    """Возвращает сотрудника уже со списком инструментов"""
    employee.tools = [
        issue.tool.tool_model
        for issue in employee.tool_issues
        if issue.tool and issue.tool.tool_model
    ]
    return employee