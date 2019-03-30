from reddit import reddit
from companies import COMPANIES

import pprint
import matplotlib.pyplot as plt


def get_intern_hourly_rates():
    salaries = {}

    for submission in reddit.subreddit('cscareerquestions') \
            .search('Salary Sharing thread intern'):
        # Make sure we're only looking at official salary sharing threads
        if '[OFFICIAL] Salary Sharing thread' not in submission.title:
            continue

        print("Collecting comments from '{0}'.".format(submission.title))

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

                # Before beginning, trim out the header section.
                # This is where people list their school and any
                # past internships or CS experience they might have
                # had. If this is not done, people can include
                # companies in here that will be incorrectly
                # considered as current offers
                header_tags = ['prior experience',
                               'past experience',
                               'previous experience',
                               'school']
                for tag in header_tags:
                    header_idx = content.find(tag)
                    if header_idx >= 0:
                        header_idx += len(tag)
                        content = content[header_idx:]
                        end_header_idx = content.find('\n')
                        content = content[end_header_idx:]

                for company in COMPANIES:
                    # Try to find each company in the user's comment
                    # If it appears, it's almost certain that it's
                    # one of the user's offers, given that the past
                    # experience header section has been filtered out
                    company_idx = content.find(company.lower())
                    if company_idx >= 0:
                        salary = -1
                        for i in range(company_idx, len(content)):
                            if content[i] == '/' and \
                                    (content[i - 1].isnumeric() or
                                     content[i - 1] == 'k') and \
                                    content[i + 1] in 'hmw':
                                # Make sure a salary label is on the same line
                                # If there's a newline between the label and
                                # the slash, then it's likely that we are
                                # looking at invalid data
                                j = i - 1
                                invalid = False
                                while True:
                                    if content[j] == '\n':
                                        # We've reached a newline before
                                        # hitting the salary label
                                        invalid = True
                                        break
                                    if content[j:i].startswith('salary'):
                                        # We've reached the salary data
                                        # with no newlines between it
                                        # and the salary slash
                                        break
                                    j -= 1
                                if invalid:
                                    break

                                # Move the left bound of our window
                                # to accomodate the numerical portion
                                # of the given salary
                                end = i
                                start = i - 1
                                while start >= 0 and \
                                        (content[start].isnumeric() or
                                         content[start] == '.' or
                                         content[start] == ',' or
                                         (content[start] == 'k' and
                                          start == i - 1)):
                                    start -= 1
                                start += 1

                                # Parse salary into a numerical result,
                                # taking into account whether it was
                                # given as an hourly, monthly, or weekly
                                # rate. Additionally, transform any -k
                                # endings by multiplying by 1000
                                salary = float(content[start:end]
                                               .replace(',', '')
                                               .replace('k', ''))
                                if content[i - 1] == 'k':
                                    salary *= 1000
                                if content[i + 1] == 'm':
                                    salary /= 160
                                if content[i + 1] == 'w':
                                    salary /= 40

                                # Intern monthly salaries should at least be
                                # in the hourly range [15, 100]. Any numbers
                                # outside those ranges are basically impossible
                                if salary < 15 or salary > 100:
                                    print("Skipping #{0} ({1}). "
                                          "Salary is ${2}/hour?"
                                          .format(comment.id, company, salary))
                                    salary = -1

                                # Correct company names so we only get one
                                # appearance of the company in the output
                                # (e.g JPMorgan and JP Morgan are the same
                                # company, just stylized differently)
                                if company == 'Google':
                                    if content in ['ep intern',
                                                   'engineering practicum'
                                                   'intern']:
                                        company = 'Google-EP'
                                if company == 'JP Morgan':
                                    company = 'JPMorgan'
                                if company == 'Digital Ocean':
                                    company = 'DigitalOcean'
                                if company in ['Proprietary Trading',
                                               'Trading Firm',
                                               'Prop Shop']:
                                    company = 'Prop Trading'
                                if company == '2 Sigma':
                                    company = 'Two Sigma'

                                break

                        if salary > 0:
                            # Base case: a company has 0 interns working
                            # for it and they pay an hourly rate of 0
                            if company not in salaries:
                                salaries[company] = [0, 0]

                            # Recompute averages and increase count
                            stats = salaries[company]
                            [avg, cnt] = stats
                            stats[0] = ((avg * cnt) + salary) / (cnt + 1)
                            stats[1] += 1
    return salaries


def display_intern_salaries():
    # Fetch salary data and pretty print it for debugging purposes
    intern_salaries = get_intern_hourly_rates()
    pprint.pprint(intern_salaries)

    # Extract x, y data (companies, rates respectively)
    companies = sorted(list(intern_salaries.keys()),
                       key=lambda c: intern_salaries[c][0])
    num_salaries = sum([intern_salaries[c][1] for c in companies])
    x = ['{0} ({1})'.format(c, intern_salaries[c][1]) for c in companies]
    y = [intern_salaries[c][0] for c in companies]
    x_pos = [i for i, _ in enumerate(x)]

    # Specify horizontal bar plot showing x-y data
    plt.style.use('ggplot')
    plt.barh(x_pos, y, color='green')
    plt.xlabel("Hourly Rate (USD/hr)")
    plt.ylabel("Companies")
    plt.title("{0} CS internship salaries "
              "(as reported by /r/cscareerquestions)".format(num_salaries))
    plt.yticks(x_pos, x)

    for i, v in enumerate(y):
        plt.text(v + 0.5, i - 0.3, '{0:.2f}'.format(v),
                 color='green', fontweight='bold')

    # Call the plot display routine
    plt.show()


if __name__ == '__main__':
    display_intern_salaries()
