COMPANIES = [
    'Facebook',
    'Apple',
    'Amazon',
    'Netflix',
    'Google',
    'Microsoft',
    'LinkedIn',
    'Twitter',
    'GitHub',
    'Bloomberg',
    'Quora',
    'MITRE',
    'IBM',
    'SAP',
    'Cisco',
    'Lyft',
    'Uber',
    'Lime',
    'Bird',
    'Airbnb',
    'Qualcomm',
    'Citadel',
    'Jane Street',
    'Two Sigma',
    '2 Sigma',
    'DRW',
    'SIG',
    'IMC',
    'AQR',
    'Bridgewater Associates',
    'Akuna Capital',
    'Virtu Financial',
    'Hudson River Trading',
    'Goldman Sachs',
    'Morgan Stanley',
    'JP Morgan',
    'JPMorgan',
    'Citi',
    'Citigroup',
    'Bank of America',
    'Capital One',
    'Barclays',
    'Hedge Fund',
    'Prop Trading',
    'Trading Firm',
    'Prop Shop',
    'Proprietary Trading',
    'HFT',
    'Fintech',
    'NASA',
    'Tesla',
    'SpaceX',
    'Intuit',
    'Yelp',
    'Yext',
    'Atlassian',
    'Telecom',
    'Square',
    'Palantir',
    'Stripe',
    'Rubrik',
    'Intel',
    'Asana',
    'VMware',
    'AT&T',
    'Oil',
    'Nvidia',
    'Blackrock',
    'Credit Karma',
    'Dropbox',
    'Box',
    'Squarespace',
    'TripAdvisor',
    'Optiver',
    'Nextdoor',
    'Redfin',
    'Zillow',
    'Workday',
    'Digital Ocean',
    'DigitalOcean',
    'Pure Storage',
    'PureStorage',
    'Datadog',
    'Shopify',
    'Zendesk',
    'PayPal',
    'Snapchat',
    'Snap',
    'Snap Inc',
    'MongoDB',
    'Salesforce',
    'Pinterest',
    'Yahoo',
    'Flexport',
    'SurveyMonkey',
    'Cruise',
    'Flatiron Health',
    'Cloudera',
    'Foursquare',
    'Tableau',
    'Riot',
    'Lockheed Martin',
    'Raytheon',
    'Boeing',
    'Northrop Grumman',
    'United Technologies',
    'Defense',
    'Insurance',
    'Oracle',
    'American Express',
    'Visa',
    'Mastercard',
    'Epic',
    'Slack',
    'Walmart Labs',
    'Nike',
    'ViaSat',
    'Coursera',
    'HubSpot',
    'Groupon',
    'Qualtrics',
    'Blend Labs',
]


def combine_synonyms(company):
    if company == 'JP Morgan':
        company = 'JPMorgan'
    if company == 'Digital Ocean':
        company = 'DigitalOcean'
    if company in ['Proprietary Trading', 'Trading Firm', 'Prop Shop']:
        company = 'Prop Trading'
    if company == '2 Sigma':
        company = 'Two Sigma'
    if company == 'Pure Storage':
        company = 'PureStorage'
    if company in ['Snapchat', 'Snap', 'Snap Inc']:
        company = 'Snap Inc.'
    if company == 'Citi':
        company = 'Citigroup'
    return company
