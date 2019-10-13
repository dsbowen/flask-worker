"""Tasks

The execute_job function is used by a Worker to execute its job (i.e. its 
Employer's complex task).

I recommend programmers copy and paste this file in the root directory of 
their application folder. Modify the name of the application file and 
instance as necessary.
"""

# 1. Import application instance
from app import app

# 2. Import execute function
from flask_worker import execute

# 3. Push the application context
app.app_context().push()

# 4. Define the execute_job function
def execute_job(**kwargs):
    return execute(**kwargs)