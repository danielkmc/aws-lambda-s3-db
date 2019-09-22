import re
import datetime
import string

"""Create a lambda function that raises an exception when certain conditions are met.
        Action: Login/Logoff
        Condition: Always
        Return: 1. Count of failed logins
                2. interactive login using service acct (dwbatch) or dba schema (failed)?

        Other:  1. Server identity (hostname or IP address)
                2. DB name
                3. Connection method
                4. Count of failed logins


        Action: DDL
        Condition: ['All DB accounts', 'ALTER', 'CREATE', 'Drop'], all users except batch/spectrum users.
        Return: 1. Timestamps
                2. UserID
                3. Terminal identity (hostname or IP address)
                4. Server identity (hostname or IP address)
                5. DB name
                6. Connection method
                7. Full details of actions performed

        Other:


        Action: DML
        Condition: ['DATABASE LINK', 'DELETE', 'INSERT', 'SELECT', 'TRIGGER', 'TRUNCATE', 'UPDATE', 'WRITE']


        Action: DCL
        Condition: ['ALTER', 'CREATE', 'DROP', 'GRANT', 'REVOKE']

"""
"""LOG: data can be separated by splicing with [' ', '(', ')', ',']"""
""""login_info = [timestamp, db, user, pid, userid, xid]
                    [3, 5, 4, 7, 4]"""

login_info = []
log_stuff = []
date = datetime.time


def _parser(data=""):
    """function used after distinguishing individual log entries

        Takes data passed to it and retrieves the date, user info, and log keywords"""

    if data == "":
        pass
    removable = (')', '(', '', '=', ',', '||', '\'', '#', '\',', '\'\'', ',\'\'')
    """set log data bounds"""
    log_data = data[data.index(']') + 8:]
    """Retrieve timestamp"""
    validate(data[:25])
    """Retrieve info within brackets"""
    within_brackets = re.search(r"\[(?<=\=)\w+\]", data)
    print('BRACKETED INFORMATION:', within_brackets[0])

    log_data = re.findall(r"[\w]+", data)
    print('LOG DATA:', log_data)
    global log_stuff, login_info
    log_stuff = log_data
    login_info = [log_data[i] for i in (7, 9, 11, 13, 15)]


def validate(date_text):
    try:
        global date
        date = datetime.datetime.strptime(date_text, '\'%Y-%m-%dT%H:%M:%SZ UTC')
        return True
    except ValueError:
        return False


def yield_matches(f):
    log = []
    for line in f:
        if validate(line[:25]):
            if len(log) > 0:
                yield "".join(log)
                log = []

        log.append(line)

    yield "".join(log)


_parser("""'2019-06-06t18:25:48Z UTC [ db=dev user=rdsdb pid=13320 userid=1 xid=392232 ]' LOG: SELECT
  e.employee_id AS "Employee #"
  , e.first_name || ' ' || e.last_name AS "Name"
  , e.email AS "Email"
  , e.phone_number AS "Phone"
  , TO_CHAR(e.hire_date, 'MM/DD/YYYY') AS "Hire Date"
  , TO_CHAR(e.salary, 'L99G999D99', 'NLS_NUMERIC_CHARACTERS = ''.,'' NLS_CURRENCY = ''$''') AS "Salary"
  , e.commission_pct AS "Comission %"
  , 'works as ' || j.job_title || ' in ' || d.department_name || ' department (manager: '
    || dm.first_name || ' ' || dm.last_name || ') and immediate supervisor: ' || m.first_name || ' ' || m.last_name AS "Current Job"
  , TO_CHAR(j.min_salary, 'L99G999D99', 'NLS_NUMERIC_CHARACTERS = ''.,'' NLS_CURRENCY = ''$''') || ' - ' ||
      TO_CHAR(j.max_salary, 'L99G999D99', 'NLS_NUMERIC_CHARACTERS = ''.,'' NLS_CURRENCY = ''$''') AS "Current Salary"
  , l.street_address || ', ' || l.postal_code || ', ' || l.city || ', ' || l.state_province || ', '
    || c.country_name || ' (' || r.region_name || ')' AS "Location"
  , jh.job_id AS "History Job ID"
  , 'worked from ' || TO_CHAR(jh.start_date, 'MM/DD/YYYY') || ' to ' || TO_CHAR(jh.end_date, 'MM/DD/YYYY') ||
    ' as ' || jj.job_title || ' in ' || dd.department_name || ' department' AS "History Job Title"

FROM employees e
-- to get title of current job_id
  JOIN jobs j
    ON e.job_id = j.job_id
-- to get name of current manager_id
  LEFT JOIN employees m
    ON e.manager_id = m.employee_id
-- to get name of current department_id
  LEFT JOIN departments d
    ON d.department_id = e.department_id
-- to get name of manager of current department
-- (not equal to current manager and can be equal to the employee itself)
  LEFT JOIN employees dm
    ON d.manager_id = dm.employee_id
-- to get name of location
  LEFT JOIN locations l
    ON d.location_id = l.location_id
  LEFT JOIN countries c
    ON l.country_id = c.country_id
  LEFT JOIN regions r
    ON c.region_id = r.region_id
-- to get job history of employee
  LEFT JOIN job_history jh
    ON e.employee_id = jh.employee_id
-- to get title of job history job_id
  LEFT JOIN jobs jj
    ON jj.job_id = jh.job_id
-- to get name of department from job history
  LEFT JOIN departments dd
    ON dd.department_id = jh.department_id
ORDER BY e.employee_id;""")

print(date)
print('login_info=', login_info)
print("log_stuff=", log_stuff)
print("\n\n\n\n")

index = 0
file = open("test_log.txt", "r")  # change this for lambda function
logs = list(yield_matches(file))

for l in logs:
    print('---------------------MATCH---------------', '\n' + l)
