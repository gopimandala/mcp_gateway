JIRA_OPERATIONS = {
    "get_issue": {
        "method": "GET",
        "path": "/rest/api/2/issue/{issue_key}",
        "trace_name": "Jira API: Fetch Issue",
        "description": "Fetch a Jira issue by key"
    },

    "add_comment": {
        "method": "POST",
        "path": "/rest/api/3/issue/{issue_key}/comment",
        "trace_name": "jira_add_comment",
        "description": "Add a comment to a Jira issue"
    }
}