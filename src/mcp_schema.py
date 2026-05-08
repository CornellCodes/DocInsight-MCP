from typing import Dict, List, Any


TOOLS: List[Dict[str, Any]] = [
    {
        "name": "get_all_applications",
        "description": "Return a list of all applications",
        "parameters": {}
    },
    {
        "name": "count_all_applications",
        "description": "Return the total number of applications",
        "parameters": {}
    },
    {
        "name": "get_application_by_id",
        "description": "Get full application details for a specific application ID",
        "parameters": {
            "app_id": "number"
        }
    },
    {
        "name": "get_applications_by_degree",
        "description": "Find applications by degree code",
        "parameters": {
            "degree_code": "string"
        }
    },
    {
        "name": "count_applications_by_degree",
        "description": "Count applications by degree code",
        "parameters": {
            "degree_code": "string"
        }
    },
    {
        "name": "get_applications_by_admission_note",
        "description": "Find applications by admission note",
        "parameters": {
            "admission_note": "string"
        }
    },
    {
        "name": "count_applications_by_admission_note",
        "description": "Count applications by admission note",
        "parameters": {
            "admission_note": "string"
        }
    },
    {
        "name": "filter_applications",
        "description": "Filter applications using one or more optional criteria",
        "parameters": {
            "degree_code": "string",
            "admission_note": "string",
            "min_gpa": "number",
            "max_gpa": "number",
            "student_type": "string",
            "term": "string"
        }
    },
    {
        "name": "get_missing_items_for_application",
        "description": "Get missing items for an application",
        "parameters": {
            "app_id": "number"
        }
    },
    {
        "name": "get_documents_for_application",
        "description": "Get documents for an application",
        "parameters": {
            "app_id": "number"
        }
    },
    {
        "name": "count_filtered_applications",
        "description": "Count applications using one or more optional criteria",
        "parameters": {
            "degree_code": "string",
            "admission_note": "string",
            "min_gpa": "number",
            "max_gpa": "number",
            "student_type": "string",
            "term": "string"
        }
    },
    {
        "name": "get_random_applicant",
        "description": "Return one random applicant",
        "parameters": {}
    },
    {
        "name": "get_applicant_admission_status",
        "description": "Get the admission decision/status for a specific applicant by name.",
        "parameters": {
            "name": "string"
        }
    },
    {
        "name": "get_applicant_term",
        "description": "Get the application term for a specific applicant by name.",
        "parameters": {
            "name": "string"
        }
    },
    {
        "name": "get_applicant_gpa",
        "description": "Get the GPA for a specific applicant by name.",
        "parameters": {
            "name": "string"
        }
    },
    {
        "name": "search_applicants_by_name",
        "description": "Find applicants whose name matches or partially matches a search query.",
        "parameters": {
            "name_query": "string"
        }
    },
    {
        "name": "get_applicant_muid",
        "description": "Get the MUID for a specific applicant by name.",
        "parameters": {
            "name": "string"
        }
    },
    {
        "name": "get_full_admission_percentage",
        "description": "Calculate the percentage of applicants who received full admission.",
        "parameters": {}
    },
    {
        "name": "get_average_gpa_for_admitted_students",
        "description": "Calculate the average GPA for admitted students, including full, conditional, and provisional admissions.",
        "parameters": {}
    },
    {
        "name": "get_major_with_highest_average_gpa",
        "description": "Find the major with the highest average applicant GPA.",
        "parameters": {}
    },
    {
        "name": "get_applicants_who_took_course",
        "description": "Find applicants who took a course by course title, subject and number, or partial course name.",
        "parameters": {
            "course_query": "string"
        }
    },
    {
        "name": "get_applicants_by_course_grade_filter",
        "description": "Find applicants based on their grade in a specific course. grade_filter can be below_b, at_least_b, a_only, exact_b, or passed.",
        "parameters": {
            "course_query": "string",
            "grade_filter": "string"
        }
    },
    {
        "name": "get_applicant_strongest_subject",
        "description": "Determine the applicant's strongest subject area based on highest average course grade.",
        "parameters": {
            "name": "string"
        }
    },
    {
        "name": "count_applicant_courses_by_subject",
        "description": "Count how many completed courses an applicant has in a specific subject, such as CS, MTH, ENG, or CMM.",
        "parameters": {
            "name": "string",
            "subject": "string"
        }
    },
    {
        "name": "get_full_profile_by_name",
        "description": "Get a full applicant profile by name, including application details, missing items, documents, and transcript courses.",
        "parameters": {
            "name": "string"
        }
    },
]


REQUIRED_ARGUMENTS: Dict[str, List[str]] = {
    "get_all_applications": [],
    "count_all_applications": [],
    "get_application_by_id": ["app_id"],
    "get_applications_by_degree": ["degree_code"],
    "count_applications_by_degree": ["degree_code"],
    "get_applications_by_admission_note": ["admission_note"],
    "count_applications_by_admission_note": ["admission_note"],
    "filter_applications": [],
    "get_missing_items_for_application": ["app_id"],
    "get_documents_for_application": ["app_id"],
    "count_filtered_applications": [],
    "get_random_applicant": [],
    "get_applicant_admission_status": ["name"],
    "get_applicant_term": ["name"],
    "get_applicant_gpa": ["name"],
    "search_applicants_by_name": ["name_query"],
    "get_applicant_muid": ["name"],
    "get_full_admission_percentage": [],
    "get_average_gpa_for_admitted_students": [],
    "get_major_with_highest_average_gpa": [],
    "get_applicants_who_took_course": ["course_query"],
    "get_applicants_by_course_grade_filter": ["course_query", "grade_filter"],
    "get_applicant_strongest_subject": ["name"],
    "count_applicant_courses_by_subject": ["name", "subject"],
    "get_full_profile_by_name": ["name"],
}


def get_tool_names() -> List[str]:
    return [tool["name"] for tool in TOOLS]


def get_tool_schema(tool_name: str) -> Dict[str, Any]:
    for tool in TOOLS:
        if tool["name"] == tool_name:
            return tool
    raise ValueError(f"Unknown tool: {tool_name}")


def get_required_arguments(tool_name: str) -> List[str]:
    if tool_name not in REQUIRED_ARGUMENTS:
        raise ValueError(f"Unknown tool: {tool_name}")
    return REQUIRED_ARGUMENTS[tool_name]
