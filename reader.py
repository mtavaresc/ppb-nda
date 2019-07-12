from docx import Document
# from json import dumps
from re import findall, sub, match
# from itertools import groupby
from base import Session, engine
from models import *


def create_or_drop_db(drop=False):
    if drop:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def extract_data_from_playbook(doc):
    issues_a, issues_b, principles_paragraph = [], [], []
    for paragraph in doc.paragraphs:
        if paragraph.text.lower().startswith('Issue'.lower()):
            if match(r'(Issue\s[#]\d+[A-Z])', paragraph.text) is not None:
                issue_paragraph = paragraph.text.split('.')[0]
                issue_id = findall(r'(Issue\s[#]\d+[A-Z])', issue_paragraph)[0]
                issue_id = issue_id[issue_id.index('#') + 1:]
                if sub(r'(Issue\s[#]\d+[A-Z])', '', issue_paragraph).split(':')[1].strip() == 'Customer’s request':
                    issue_name = sub(r'(Issue\s[#]\d+[A-Z])', '', issue_paragraph).split(':')[2].strip()
                else:
                    issue_name = sub(r'(Issue\s[#]\d+[A-Z])', '', issue_paragraph).split(':')[1].strip()
                issues_b.append((issue_id, issue_name))
            else:
                issue_paragraph = paragraph.text.split('.')[0].strip()
                issue_id = issue_paragraph[issue_paragraph.index('#') + 1:issue_paragraph.index(':')]
                issue_name = issue_paragraph.split(':')[1].strip()
                issues_a.append((issue_id, issue_name))
        elif paragraph.text.lower().startswith('Customer’s request'.lower()):
            cr = paragraph.text.split(':')[1].strip()
            cr_dict = {
                'id': 'A',
                'customer_request': cr
            }
            tup = issues_a[-1] + ([cr_dict],)
            issues_a.pop()
            issues_a.append(tup)

    for idx, a in enumerate(issues_a):
        list_of_cr_dict = []
        for b in issues_b:
            if a[0] == b[0][:-1]:
                cr_dict = {
                    'id': b[0][-1:],
                    'customer_request': b[1]
                }
                list_of_cr_dict.append(cr_dict)
        if len(list_of_cr_dict) > 0:
            tup = a + (list_of_cr_dict,)
            issues_a[idx] = tup

    found = False
    for paragraph in doc.paragraphs:
        next_topic = ['Sample Language', 'Dell EMC Standard Language', 'Fallback', 'Approval']
        if paragraph.text.lower().startswith('Principle'.lower()):
            if len(paragraph.text.split(':')[1].strip()) > 0:
                found = True

        if found:
            if any(paragraph.text.lower().startswith(word.lower()) for word in next_topic) is False \
                    and paragraph.text != '':
                principles_paragraph.append(sub(r'(Principle+?)(s\b|\b)[:]', '', paragraph.text).strip())

        if any(paragraph.text.lower().startswith(word.lower()) for word in next_topic):
            break

    principles = '\n'.join(principles_paragraph)
    print(principles)

    return issues_a


def insert_db(issues):
    s = Session()
    # for j in list(a for a, _ in groupby(a)):
    for i in issues:
        issue = i[0]
        name = i[1]
        list_of_dict_cr = i[2]
        try:
            s.merge(Issues(issue, name))
            for dict_cr in list_of_dict_cr:
                s.merge(CustomersRequest(issue, dict_cr['id'], dict_cr['customer_request'], principles=''))

            s.commit()
        except Exception as e:
            print(f'#1 Error: {e}')
            return False

    return True


if __name__ == '__main__':
    document = Document('samples/playbook_nda.docx')
    # create_or_drop_db()
    rs = extract_data_from_playbook(document)
    # print(dumps(rs, indent=4))
    # insert_db(rs)
