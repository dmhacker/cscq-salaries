from reddit import reddit
from companies import COMPANIES, combine_synonyms

import statistics
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


def get_intern_offers(logger=global_logger):
    offers = []

    def extract_labeled_line(content, label):
        label_idx = content.find(label, company_idx)
        if label_idx == -1:
            return (-1, -1)
        line_start = label_idx
        while line_start >= 0 and \
                content[line_start] != '\n':
            line_start -= 1
        line_start += 1
        line_end = label_idx
        while line_end < len(content) and \
                content[line_end] != '\n':
            line_end += 1
        return (line_start, line_end)

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
                        (salary_start, salary_end) = \
                            extract_labeled_line(content, 'salary')
                        if salary_start == -1:
                            continue
                        salary_line = content[salary_start:salary_end]

                        # Skip to last appearance of label keyword,
                        # fixes issues with Datadog comment
                        i = salary_line.find('salary') + len('salary')

                        # Extract the first numeric value in the
                        # salary line
                        salary_buffer = ''
                        mode = 0
                        for i in range(len(salary_line)):
                            c = salary_line[i]
                            if mode == 0:
                                if c.isnumeric():
                                    salary_buffer += c
                                    mode = 1
                            elif mode == 1:
                                if c.isnumeric() or \
                                        c == 'k' or \
                                        c == '.' or \
                                        c == ',':
                                    salary_buffer += c
                                else:
                                    break

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
                        salary_remainder = salary_line[i:]
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
                                salary_remainder.startswith('/2') or \
                                salary_remainder.startswith('$/2') or \
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

                        # Identify the location line
                        (loc_start, loc_end) = \
                            extract_labeled_line(content, 'location:')
                        if loc_start == -1:
                            continue
                        loc_line = content[loc_start:loc_end]

                        # Trim out the label and any formatting from
                        # the locaiton line
                        loc_actual_start = loc_line.find('location:') \
                            + len('location:')
                        location = loc_line[loc_actual_start:loc_end] \
                            .replace('**', '').strip()

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
                            if 'explorer intern' in content or \
                                    'explore intern' in content:
                                company = 'Microsoft-Explore'

                        # Add to list of salaries for company
                        offers.append({
                            'company': company,
                            'salary': salary,
                            'location': location
                        })

    return sorted(offers, key=lambda o: (o['company'], o['salary']))


def display_intern_salaries():
    # Collect raw offer data
    offers = get_intern_offers()
    print(json.dumps(offers, indent=2, sort_keys=True))

    # Convert offers to salaries by companies
    salaries = {}
    for offer in offers:
        company = offer['company']
        salary = offer['salary']
        if company in salaries:
            salaries[company].append(salary)
        else:
            salaries[company] = [salary]

    # Fetch salary data and pretty print it for debugging purposes
    average_salaries = {c: statistics.mean(salaries[c])
                        for c in salaries.keys()}

    # Extract x, y data (companies, rates respectively)
    companies = sorted(list(salaries.keys()),
                       key=lambda c: average_salaries[c])
    x = ['{0}'.format(c) for c in companies]
    y = [average_salaries[c] for c in companies]
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
