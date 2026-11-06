# School-holiday closure counts for /is-there-school-on/ pages.
#
# Sample: the largest district listed for each state in build-states/states_data.py (the first
# entry of its `districts` list). DC uses DC Public Schools.
# Method: each district's published 2026-27 student calendar was read on RETRIEVED. A day counts as
# "closed" when the calendar marks it "no school" for students (holiday, election day, teacher
# workday or professional development); "remote" when it is a scheduled virtual / remote learning
# day; "open" when the calendar lists no closure for that date. Calendars were read through
# agendahero.com, which republishes each district's calendar as dated events and links the
# district's own site; NYC was also checked on schools.nyc.gov.
# Not confirmed: Vermont (Burlington School District calendar not found), and Election Day for
# Portland Public Schools (Maine) — these are left out of the counts, never guessed.
#
# Edit a row, re-run build-holidays/build_holidays.py; the page's dateModified only moves when the
# rendered content changes.

RETRIEVED = "2026-11-06"
SCHOOL_YEAR = "2026-27"
AH = "https://agendahero.com/page/"

# state, district, election_day_2026 (Nov 3), veterans_day_2026 (Nov 11), calendar label for the
# closure (as written on the calendar), source page
ROWS = [
 ("AL", "Mobile County Public Schools",        "remote", "closed", "Veterans Day (system-wide holiday); Election Day virtual learning", AH + "al-mobile-county-public-schools-2026-27"),
 ("AR", "Little Rock School District",         "open",   "open",   "", AH + "ar-little-rock-school-district-2026-27"),
 ("CO", "Denver Public Schools",               "open",   "open",   "", AH + "co-denver-2026-27"),
 ("CT", "Hartford Public Schools",             "closed", "closed", "Veterans' Day; Election Day professional learning", AH + "ct-hartford-school-district-2026-27"),
 ("DC", "DC Public Schools",                   "closed", "closed", "Veterans Day; Election Day", AH + "dc-public-schools-2026-27"),
 ("DE", "Christina School District",           "closed", "closed", "Veterans Day; Election Day", AH + "de-christina-school-district-2026-27"),
 ("GA", "Gwinnett County Public Schools",      "remote", "open",   "Election Day digital learning day", AH + "ga-gwinnett-county-2026-27"),
 ("IA", "Des Moines Public Schools",           "closed", "open",   "Election Day", AH + "ia-des-moines-2026-27"),
 ("ID", "West Ada School District",            "closed", "open",   "Election Day professional learning", AH + "id-west-ada-2026-27"),
 ("IL", "Chicago Public Schools",              "closed", "closed", "General Election Day; Veterans Day professional development (no students)", AH + "il-chicago-2026-27"),
 ("IN", "Indianapolis Public Schools",         "closed", "open",   "Election Day staff professional development", AH + "in-indianapolis-public-schools-2026-27"),
 ("KS", "Wichita Public Schools USD 259",      "closed", "open",   "Election Day district inservice", AH + "ks-usd259-wichita-2026-27"),
 ("KY", "Jefferson County Public Schools",     "closed", "open",   "Election Day", AH + "ky-jefferson-2026-27"),
 ("MA", "Boston Public Schools",               "open",   "closed", "Veterans Day", AH + "ma-boston-2026-27"),
 ("MD", "Montgomery County Public Schools",    "closed", "open",   "Election Day", AH + "md-montgomery-county-traditional-2026-27"),
 ("ME", "Portland Public Schools",             None,     "closed", "Veterans Day", "https://calendarstates.com/maine/portland-public-schools/"),
 ("MI", "Detroit Public Schools Community District", "closed", "open", "Election Day professional development", AH + "mi-detroit-public-schools-community-district-2026-27"),
 ("MN", "Anoka-Hennepin Schools",              "closed", "open",   "Election Day staff development", AH + "mn-anoka-hennepin-2026-27"),
 ("MO", "Springfield Public Schools",          "closed", "open",   "Professional Day / Election Day", AH + "mo-springfield-2026-27"),
 ("MT", "Billings Public Schools",             "open",   "open",   "", AH + "mt-billings-public-schools-2026-27"),
 ("NC", "Wake County Public School System",    "closed", "closed", "Veterans Day holiday; Election Day teacher workday", AH + "nc-wake-county-schools-2026-27"),
 ("ND", "Fargo Public Schools",                "open",   "closed", "Veterans Day holiday", AH + "nd-fargo-1-2026-27"),
 ("NE", "Omaha Public Schools",                "closed", "open",   "Election Day (no school for all students)", AH + "ne-omaha-2026-27"),
 ("NH", "Manchester School District",          "closed", "closed", "Veterans' Day; Election Day", AH + "nh-manchester-school-district-2026-27"),
 ("NJ", "Newark Public Schools",               "open",   "closed", "Veterans Day", AH + "nj-newark-public-school-district-2026-27"),
 ("NM", "Albuquerque Public Schools",          "closed", "closed", "Veterans Day; Election Day", AH + "nm-albuquerque-public-schools-2026-27"),
 ("NY", "New York City Public Schools",        "remote", "closed", "Veterans Day; Election Day remote learning", AH + "ny-new-york-city-public-schools-2026-27"),
 ("OH", "Columbus City Schools",               "closed", "open",   "Election Day professional development", AH + "oh-columbus-city-2026-27"),
 ("OK", "Oklahoma City Public Schools",        "open",   "open",   "", AH + "ok-oklahoma-city-ps-2026-27"),
 ("OR", "Portland Public Schools",             "open",   "open",   "", AH + "or-portland-2026-27"),
 ("PA", "School District of Philadelphia",     "closed", "closed", "Veterans Day; Election Day", AH + "pa-philadelphia-city-sd-2026-27"),
 ("RI", "Providence Public Schools",           "closed", "closed", "Veterans Day; Election Day", AH + "ri-providence-public-schools-2026-27"),
 ("SC", "Greenville County Schools",           "closed", "open",   "Election Day", AH + "sc-greenville-2026-27"),
 ("SD", "Sioux Falls School District",         "open",   "closed", "Veterans' Day observance", AH + "sd-sioux-falls-school-district-49-5-2026-27"),
 ("TN", "Memphis-Shelby County Schools",       "open",   "closed", "Veterans Day", AH + "tn-shelby-county-2026-27"),
 ("TX", "Houston ISD",                         "open",   "open",   "", AH + "tx-houston-isd-2026-27"),
 ("UT", "Alpine School District",              "open",   "open",   "", AH + "ut-alpine-district-2026-27"),
 ("VA", "Fairfax County Public Schools",       "closed", "open",   "Election Day school planning day", AH + "va-fairfax-county-2026-27"),
 ("WA", "Seattle Public Schools",              "open",   "closed", "Veterans Day observed", AH + "wa-seattle-2026-27"),
 ("WI", "Milwaukee Public Schools",            "closed", "open",   "Election Day professional development", AH + "wi-milwaukee-2026-27"),
 ("WV", "Kanawha County Schools",              "closed", "closed", "Veterans Day; Election Day", AH + "wv-kanawha-county-schools-2026-27"),
]

# which ROWS column each holiday page uses, and the date it describes
FIELD = {"election-day": (2, "2026-11-03"), "veterans-day": (3, "2026-11-11")}
