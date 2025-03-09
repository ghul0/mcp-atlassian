
import os
from dotenv import load_dotenv

load_dotenv()

print("JIRA_URL:", os.getenv("JIRA_URL"))
print("JIRA_USERNAME:", os.getenv("JIRA_USERNAME"))
print("JIRA_API_TOKEN:", os.getenv("JIRA_API_TOKEN"))
