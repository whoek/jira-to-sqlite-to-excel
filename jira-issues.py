from jira.client import JIRA
import pandas as pd
import sqlite3
import xlsxwriter

# Settings
email = 'name@domain.com'                    # Jira username
api_token = "wlBnubFKBPYCQ8NQFb377407"       # Jira API token
server = 'https://kk2000.atlassian.net/'     # Jira server URL
jql = "project = KK"                         # JQL 

# Get issues from Jira
jira = JIRA(options={'server': server}, basic_auth= (email, api_token))
jira_issues = jira.search_issues(jql,maxResults=0)

# JSON to SQLite
issues = pd.DataFrame()
for issue in jira_issues:
    d = {
        'id': issue.id ,
        'key': issue.key,
        'assignee': str(issue.fields.assignee),
        'creator' : str(issue.fields.creator),
        'reporter': str(issue.fields.reporter),
        'created' : str(issue.fields.created),   
        'labels': str(issue.fields.labels),
        'components': str(issue.fields.components),
        'description': str(issue.fields.description),
        'summary': str(issue.fields.summary),
        'fixVersions': str(issue.fields.fixVersions),
        'subtask': str(issue.fields.issuetype.subtask),
        'issuetype': str(issue.fields.issuetype.name),
        'priority': str(issue.fields.priority.name),
        'project': str(issue.fields.project),
        'resolution': str(issue.fields.resolution),
        'resolution_date': str(issue.fields.resolutiondate),
        'status': str(issue.fields.status.name),
        'status_description': str(issue.fields.status.description),
        'updated': str(issue.fields.updated),
        'versions': str(issue.fields.versions),
        'watchcount': str(issue.fields.watches.watchCount),
    }
    issues = issues.append(d, ignore_index=True)    
    
con = sqlite3.connect("jira-issues.db")
issues.to_sql("issues", con, if_exists="replace")
con.close() 

# Get data from SQLite
con = sqlite3.connect("jira-issues.db")
sql = "select issuetype, count(*) count from issues group by issuetype"
df = pd.read_sql_query(sql, con)
con.close() 

# Create Excel file
row = 1
col = 1
workbook = xlsxwriter.Workbook('jira-excel.xlsx')
header = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#D8E4BC'})
center = workbook.add_format({'align': 'center'})
worksheet = workbook.add_worksheet('Summary')
worksheet.write(row, col, 'Issue Type', header)
worksheet.write(row, col + 1, 'Count', header)
row += 1
for index, dat in df.iterrows():
    worksheet.write(row + index, col, dat['issuetype'])
    worksheet.write(row + index, col + 1, int(dat['count']), center)
workbook.close()

print('All done!')
