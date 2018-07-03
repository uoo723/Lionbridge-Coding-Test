# flake8: noqa
"""
$ python p1.py < p1.txt
"""
import sys


def check_parentheses_pair(parentheses):
    answer = None
    l = []
    for c in parentheses:
        if c == '(':
            l.append(c)
        else:
            try:
                l.pop()
            except IndexError:
                answer = False
                break
    if answer is None:
        answer = True if len(l) == 0 else False

    return answer


def run(test_cases):
    for test_case in test_cases:
        answer = check_parentheses_pair(test_case)
        print(str(answer).lower())


if __name__ == '__main__':
    test_cases = []
    for line in sys.stdin:
        test_cases.append(line.replace('\n', ''))
    run(test_cases)
