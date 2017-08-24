from wlkt import login, base_url
import requests
from bs4 import BeautifulSoup
import sys

grade_url = base_url + '/' + 'student/chengji.aspx'

def get_grade(username, password, academic_year=None, term=1, course_type=None):
    """
    Get concrete course grade according to different request data(such as: academic year, term,
    etc. from NUIST.

    Default Web page will load all course grades, system will response to you when students use
    different cases to requests or submit data.
    """
    grade_list = header_list = []
    nuist = login(username, password)
    if not isinstance(nuist, requests.sessions.Session):
        sys.exit()

    soup = BeautifulSoup(nuist.get(grade_url).text, 'html.parser')
    whoami = soup.p.string.strip().split(',')[0]

    # TODO: support getting fail in the exams info, list[0] is passing in the exams.
    grade_result = soup.find_all('table', border="1")[0].contents

    header_strings = grade_result[1]
    header_list = [header for header in header_strings.strings if header != '\n']

    # Strip new line and only get useful data info.
    resultSet = grade_result[2:][:-1]
    for grade_strings in resultSet:
        grade_list.append([grade for grade in grade_strings.strings if grade != '\n'])

    return header_list, grade_list

def pretty_table(keywords):
    header_list, grade_list, *_ = keywords
    # Print table header using tab as delimiter
    for header_index in range(8):
        print(header_list[header_index], end='\t\t')

    print('', flush=True)
    # Print table body
    for grade_index in range(len(grade_list)):
        print('--' * 80)
        for index in range(8):
            print(grade_list[grade_index][index], end='\t', flush=True)
            index += 1
        print('')

if __name__ == '__main__':
    username = input('INFO: please input your Student Number ---> ')
    password = input('INFO: please input your Password ---> ')

    pretty_table(get_grade(username, password))
