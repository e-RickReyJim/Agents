"""Citation format templates for scientific papers"""

CITATION_FORMATS = {
    'IEEE': {
        'name': 'IEEE',
        'description': 'Institute of Electrical and Electronics Engineers',
        'in_text': '[N]',
        'reference_format': '[N] Authors, "Title," Journal, vol. X, no. Y, pp. Z, Year.',
        'example': '[1] A. Author and B. Coauthor, "Article Title," Journal Name, vol. 10, no. 2, pp. 123-456, 2023.'
    },
    'APA': {
        'name': 'APA 7th',
        'description': 'American Psychological Association (7th edition)',
        'in_text': '(Authors, Year)',
        'reference_format': 'Authors (Year). Title. Journal, Volume(Issue), Pages. DOI',
        'example': 'Smith, J., & Doe, A. (2023). Article title. Journal Name, 10(2), 123-456. https://doi.org/10.1234/example'
    },
    'Vancouver': {
        'name': 'Vancouver',
        'description': 'International Committee of Medical Journal Editors',
        'in_text': '(N)',
        'reference_format': 'N. Authors. Title. Journal. Year;Volume(Issue):Pages.',
        'example': '1. Smith J, Doe A. Article title. Journal Name. 2023;10(2):123-456.'
    }
}
