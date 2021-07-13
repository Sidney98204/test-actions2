import pandas as pd
import numpy as np
import io

def reviewers_csv_to_json(reviewers_csv):
    reviewers_df = pd.read_csv(io.StringIO(reviewers_csv))
    reviewers_df.replace(np.nan, "", inplace=True)
    res = {}
    for index, row in reviewers_df.iterrows():
        linear_info = {"project_key": row["linear_project_key"], "linear_id": row["linear_user_id"]}
        jira_info = {"project_key": row["jira_project_key"], "jira_id": row["jira_user_id"]}
        reviewer_info = {
                "jira": jira_info, 
                "linear": linear_info
        }
        res[row["github_username"]] = reviewer_info
    return res



with open(".github/reviewers-info.csv") as f:
    contents = f.read()

print(contents)

print(reviewers_csv_to_json(contents))

