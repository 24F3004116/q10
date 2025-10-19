import re
import json
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

# 1. Initialize FastAPI App
app = FastAPI(
    title="TechNova Digital Assistant",
    description="API for parsing natural language queries into function calls.",
)

# 2. Add CORS Middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# 3. Define the parsing rules
# We use a list of tuples: (regex_pattern, function_name, [arg_names], [arg_types])
# The order of rules matters if queries are ambiguous (though here they are not).
FUNCTION_RULES = [
    (
        # Query: "What is the status of ticket 83742?"
        re.compile(r"What is the status of ticket (\d+)\?"),
        "get_ticket_status",
        ["ticket_id"],
        [int]
    ),
    (
        # Query: "Schedule a meeting on 2025-02-15 at 14:00 in Room A."
        re.compile(r"Schedule a meeting on ([\d\-]+) at ([\d:]+) in (.*)\."),
        "schedule_meeting",
        ["date", "time", "meeting_room"],
        [str, str, str]
    ),
    (
        # Query: "Show my expense balance for employee 10056."
        re.compile(r"Show my expense balance for employee (\d+)\."),
        "get_expense_balance",
        ["employee_id"],
        [int]
    ),
    (
        # Query: "Calculate performance bonus for employee 10056 for 2025."
        re.compile(r"Calculate performance bonus for employee (\d+) for (\d{4})\."),
        "calculate_performance_bonus",
        ["employee_id", "current_year"],
        [int, int]
    ),
    (
        # Query: "Report office issue 45321 for the Facilities department."
        re.compile(r"Report office issue (\d+) for the (.*) department\."),
        "report_office_issue",
        ["issue_code", "department"],
        [int, str]
    )
]

# 4. Define the API Endpoint
@app.get("/execute")
async def execute_query(q: Optional[str] = Query(None)):
    """
    Parses a natural language query 'q' and returns a structured
    function call JSON.
    """
    if q is None:
        raise HTTPException(status_code=400, detail="Missing query parameter 'q'")

    for pattern, func_name, arg_names, arg_types in FUNCTION_RULES:
        match = pattern.match(q)
        
        if match:
            # We found a matching rule. Extract values.
            extracted_values = match.groups()
            
            # Use an ordered dict (default in Python 3.7+)
            # to respect argument order.
            arguments = {}
            try:
                for i, name in enumerate(arg_names):
                    # Cast the extracted string value to the correct type
                    arguments[name] = arg_types[i](extracted_values[i])
            except (ValueError, IndexError):
                raise HTTPException(status_code=400, detail="Parameter type mismatch")

            # Return the required JSON format
            return {
                "name": func_name,
                "arguments": json.dumps(arguments)
            }

    # If no pattern matched
    raise HTTPException(status_code=404, detail="No matching function found for the query")

# 5. (Optional) Run the app with uvicorn
if __name__ == "__main__":
    import uvicorn
    print("--- Starting TechNova Assistant API ---")
    print("Access at: http://127.0.0.1:8000/execute")
    print("Test with: http://127.0.0.1:8000/execute?q=What+is+the+status+of+ticket+83742?")
    uvicorn.run(app, host="127.0.0.1", port=8000)