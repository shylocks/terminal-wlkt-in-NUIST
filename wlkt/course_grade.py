from wlkt import login, base_url
import requests
from bs4 import BeautifulSoup
import sys

grade_url = base_url.replace('default.aspx','student/chengji.aspx')
http_headers = { 'Accept': '*/*','Connection': 'keep-alive', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36'}

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

    soup = BeautifulSoup(nuist.get(grade_url, headers=http_headers).text, 'html.parser')
    whoami = soup.p.string.strip().split(',')[0][:-2]

    # TODO: support getting fail in the exams info, list[0] is passing in the exams.
    grade_result = soup.find_all('table', border="1")[0].contents

    header_strings = grade_result[1]
    header_list = [header for header in header_strings.strings if header != '\n']

    # Strip new line and only get useful data info.
    resultSet = grade_result[2:][:-1]
    for grade_strings in resultSet:
        grade_list.append([grade for grade in grade_strings.strings if grade != '\n'])

    return header_list, whoami, grade_list

def pretty_table(keywords):
    header_list, whoami, grade_list = keywords

    print('\n'*2)
    print('--'*35 + whoami + '--'*35, end='\t\t')
    print('')
    # Print table header using tab as delimiter, and make long string put in the send
    for header_index in range(8):
        if header_index == 2:
            continue
        print(header_list[header_index], end='\t\t')
        if header_index == 7:
            print(header_list[2], end='\t\t')

    print('')
    # Print table body
    for grade_index in range(len(grade_list)):
        print('--' * 90)
        for index in range(8):
            if index == 2:
                continue
            elif index == 1 or index == 3:
                print(grade_list[grade_index][index], end='\t'*2)
            elif index == 4:
                print(grade_list[grade_index][index], end='\t'*7)
            elif index == 7:
                print(grade_list[grade_index][index], end='\t'*2)
            else:
                print(grade_list[grade_index][index], end='\t')
            if index == 7:
                print(grade_list[grade_index][2], end='\t')
            index += 1
        print('')

if __name__ == '__main__':
    username = input('INFO: please input your Student Number ---> ')
    password = input('INFO: please input your Password ---> ')

    pretty_table(get_grade(username, password))
