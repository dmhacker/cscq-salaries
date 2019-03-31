from reddit import reddit
from companies import COMPANIES, combine_synonyms

import logging
import json

import matplotlib.pyplot as plt

LOG_FORMAT = '%(module)s - %(asctime)-15s - %(levelname)s: %(message)s'
LOG_LEVEL = logging.INFO

global_logger = logging.getLogger('cscqsal')
global_logger.handles = []
global_logger.disabled = False
handler = logging.StreamHandler()
formatter = logging.Formatter(LOG_FORMAT)
handler.setFormatter(formatter)
global_logger.addHandler(handler)
global_logger.setLevel(LOG_LEVEL)


def get_intern_hourly_rates(logger=global_logger):
    salaries = {}

    for submission in reddit.subreddit('cscareerquestions') \
            .search('Salary Sharing thread intern'):
        # Make sure we're only looking at official salary sharing threads
        if '[OFFICIAL] Salary Sharing thread' not in submission.title:
            continue

        logger.info("Collecting comments from '{0}'.".format(submission.title))

        # Do not expand any comments into the top level list
        submission.comments.replace_more(limit=0, threshold=0)

        for region_comment in submission.comments:
            # These salaries are for US internships only
            region = region_comment.body
            if 'Region -' not in region or 'US' not in region:
                continue

            for comment in region_comment.replies:
                # Convert the comment to lowercase and fix
                # trailing spaces before and after each slash
                # (interferes with salary collection later)
                content = comment.body \
                    .lower() \
                    .replace(' /', '/') \
                    .replace('/ ', '/')

                # Before beginning, trim out any lines mentioning
                # schools or past experiences. If this is not done,
                # people can include companies in here that
                # will be incorrectly considered as current offers
                trimmed_content = []
                for line in content.split('\n'):
                    good_line = True
                    for tag in ['prior experience',
                                'past experience',
                                'previous experience',
                                'school',
                                'college']:
                        if tag in line:
                            good_line = False
                            break
                    if good_line and len(line.strip()) > 0:
                        trimmed_content.append(line)
                content = '\n'.join(trimmed_content)

                for company in COMPANIES:
                    # Try to find each company in the user's comment
                    # If it appears, it's almost certain that it's
                    # one of the user's offers, given that the past
                    # experience header section has been filtered out
                    company_idx = content.find(company.lower())

                    # When a company name appears in a user's post,
                    # it must be a word within itself (surrounded by
                    # appropriate delimiters)
                    before_char = content[company_idx - 1] \
                        if company_idx > 0 else ' '
                    after_char = content[company_idx + len(company)] \
                        if company_idx + len(company) < len(content) else ' '
                    ending_delimiters = [' ', '\n', ':', '*',
                                         '/', '(', ')', '.']
                    if company_idx >= 0 and \
                            before_char in ending_delimiters and \
                            after_char in ending_delimiters:
                        # Identify the salary line for the company
                        # Usually, these lines are labeled with the
                        # 'salary' keyword
                        salary_idx = content.find('salary', company_idx)
                        if salary_idx == -1:
                            continue

                        # Find the inclusive start of the salary line
                        salary_start = salary_idx
                        while salary_start >= 0 and \
                                content[salary_start] != '\n':
                            salary_start -= 1
                        salary_start += 1

                        # Find the exclusive end of the salary line
                        salary_end = salary_idx
                        while salary_end < len(content) and \
                                content[salary_end] != '\n':
                            salary_end += 1

                        # Extract the first numeric value in the
                        # salary line. We can skip to the last
                        # appearance of the 'salary' keyword in
                        # the line before we begin searching
                        # (fixes issues with Datadog comment)
                        i = content[(salary_start + 1):salary_end] \
                            .find('salary')
                        i = i + salary_start + 1 if i >= 0 else salary_start
                        salary_buffer = ''
                        mode = 0
                        while i < salary_end:
                            if mode == 0:
                                if content[i].isnumeric():
                                    salary_buffer += content[i]
                                    mode = 1
                            elif mode == 1:
                                if content[i].isnumeric() or \
                                        content[i] == 'k' or \
                                        content[i] == '.' or \
                                        content[i] == ',':
                                    salary_buffer += content[i]
                                else:
                                    break
                            i += 1

                        # No numeric salary information
                        # could be extracted
                        if not salary_buffer:
                            continue

                        # Convert salary string into
                        # an actual float
                        salary = float(salary_buffer
                                       .replace(',', '')
                                       .replace('k', ''))
                        if salary_buffer[-1] == 'k':
                            salary *= 1000

                        # Convert all salaries into hourly rates
                        # using the immediate suffixes to the numeric
                        # portion of the salary
                        salary_remainder = content[i:salary_end]
                        if salary_remainder.startswith('/y') or \
                                salary_remainder.startswith('$/y') or \
                                salary_remainder.startswith(' per-annum') or \
                                salary_remainder.startswith(' pro-rated') or \
                                salary_remainder.startswith(' prorated') or \
                                salary_remainder.startswith(' annual'):
                            salary /= 2080
                        elif salary_remainder.startswith('/m') or \
                                salary_remainder.startswith('$/m') or \
                                salary_remainder.startswith('pm') or \
                                salary_remainder.startswith(' per mo') or \
                                salary_remainder.startswith(' monthly') or \
                                salary_remainder.startswith(' a mo') or \
                                salary_remainder.startswith(' usd/m'):
                            salary /= 174
                        elif salary_remainder.startswith('/b') or \
                                salary_remainder.startswith(' bi') or \
                                salary_remainder.startswith('$/b'):
                            salary /= 80
                        elif salary_remainder.startswith('/w') or \
                                salary_remainder.startswith('/2 weeks') or \
                                salary_remainder.startswith(' weekly') or \
                                salary_remainder.startswith(' per week') or \
                                salary_remainder.startswith(' a week') or \
                                salary_remainder.startswith(' per wk') or \
                                salary_remainder.startswith(' a wk') or \
                                salary_remainder.startswith(' usd/w') or \
                                salary_remainder.startswith('$/w'):
                            salary /= 40
                        elif salary_remainder.startswith('/h') or \
                                salary_remainder.startswith(' hr') or \
                                salary_remainder.startswith(' per hr') or \
                                salary_remainder.startswith(' an hr') or \
                                salary_remainder.startswith(' per hour') or \
                                salary_remainder.startswith(' an hour') or \
                                salary_remainder.startswith(' usd/h') or \
                                salary_remainder.startswith('$/h'):
                            pass
                        else:
                            message = ("Skipping ${0} ({1}). "
                                       "Unable to interpret '{2}{3}'.") \
                                .format(comment.id, company,
                                        salary, salary_remainder)
                            logger.warning(message)
                            continue

                        # Intern monthly salaries should at least be
                        # in the hourly range [10, 150]. Any numbers
                        # outside those ranges are basically impossible
                        if salary < 10 or salary > 150:
                            message = ("Skipping #{0} ({1}). "
                                       "Out of acceptable range: "
                                       "${2}/hour.") \
                                .format(comment.id, company, salary)
                            logger.warning(message)
                            continue

                        # Correct company names so we only get one
                        # appearance of the company in the output
                        # (e.g JPMorgan and JP Morgan are the same
                        # company, just stylized differently)
                        company = combine_synonyms(company)

                        # Handle the ridiculuous diveristy
                        # initiatives that some companies love
                        if company == 'Google':
                            if 'engineering practicum intern' \
                                    in content or \
                                    'ep intern' in content:
                                company = 'Google-EP'
                        if company == 'Facebook':
                            if 'university intern' in content:
                                company = 'Facebook-University'
                        if company == 'Microsoft':
                            if 'explore intern' in content:
                                company = 'Microsoft-Explore'

                        # Base case: a company has 0 interns working
                        # for it and they pay an hourly rate of 0
                        if company not in salaries:
                            salaries[company] = [0, 0]

                        # Recompute averages and increase count
                        stats = salaries[company]
                        [avg, cnt] = stats
                        stats[0] = (avg * cnt + salary) / (cnt + 1)
                        stats[1] += 1
    return salaries


def display_intern_salaries():
    # Fetch salary data and pretty print it for debugging purposes
    intern_salaries = get_intern_hourly_rates()
    print(json.dumps(intern_salaries, indent=2, sort_keys=True))

    # Extract x, y data (companies, rates respectively)
    companies = sorted(list(intern_salaries.keys()),
                       key=lambda c: intern_salaries[c][0])
    x = ['{0}'.format(c) for c in companies]
    y = [intern_salaries[c][0] for c in companies]
    x_pos = [i for i, _ in enumerate(x)]

    # Specify horizontal bar plot showing x-y data
    plt.style.use('ggplot')
    plt.barh(x_pos, y, color='green')
    plt.xlabel("Hourly Rate (USD/hr)")
    plt.ylabel("Companies")
    plt.title("Internship salaries for {0} companies "
              "(as reported by /r/cscareerquestions), 2016 - Present"
              .format(len(companies)))
    plt.yticks(x_pos, x)

    # Add secondary labels showing value of bars
    for i, v in enumerate(y):
        plt.text(0.5, i - 0.35, '{0:.2f}'.format(v),
                 color='white', fontsize=8, fontweight='bold')

    # Call the plot display routine
    plt.show()


if __name__ == '__main__':
    display_intern_salaries()
