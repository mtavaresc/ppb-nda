from docx import Document
from json import dumps
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
    current_tag = None
    for paragraph in doc.paragraphs:
        if paragraph.text.lower().startswith('Issue'.lower()):
            current_tag = 'Issue'
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
            current_tag = 'Customer’s request'
            cr = paragraph.text.split(':')[1].strip()
            cr_dict = {
                'id': 'A',
                'customer_request': cr
            }
            tup = issues_a[-1] + (cr_dict,)
            issues_a.pop()
            issues_a.append(tup)
        elif paragraph.text.lower().startswith('Principle'.lower()):
            current_tag = 'Principle'
            principles_paragraph.append(paragraph.text.split(':')[1].strip())

        next_topic = ['Sample Language', 'Dell EMC Standard Language', 'Fallback', 'Approval', 'Section', 'Playbook']
        if len(principles_paragraph) > 0:
            if any(paragraph.text.lower().startswith(word.lower()) for word in next_topic) is False:
                if current_tag == 'Principle':
                    principles_paragraph.append(paragraph.text.split(':')[1].strip())
                    print(paragraph.text.split(':')[1].strip())
            else:
                current_tag = [paragraph.text.lower().startswith(word.lower()) for word in next_topic][0]

        principles = ''.join(principles_paragraph)

        try:
            if issues_a[-1][0] > issues_b[-1][0][-1:]:
                tup = issues_a[-1] + (principles,)
                issues_a.pop()
                issues_a.append(tup)
            else:
                tup = issues_b[-1] + (principles,)
                issues_b.pop()
                issues_b.append(tup)
        except IndexError:
            continue
        except Exception as e:
            print(f'Test Error: {e}')
    for a in issues_a:
        for b in a:
            print(b)
        break
    return issues_a, issues_b


def insert_db(issues_a, issues_b):
    s = Session()
    # for j in list(a for a, _ in groupby(a)):
    for a in issues_a:
        try:
            i = Issues(issue=a[0], name=a[1])
            cr = CustomersRequest(issue=a[0], idx=a[2]['id'], customer_request=a[2]['customer_request'], principles='')
            s.merge(i)
            s.merge(cr)
            s.commit()
        except IndexError:
            for b in issues_b:
                if a[0] == findall(r'\d+', b[0])[0]:
                    s.merge(CustomersRequest(issue=a[0], idx=b[0][-1:], customer_request=b[1], principles=''))
                    try:
                        s.commit()
                    except Exception as e:
                        print(f'#2 Error: {e}')
                        return False
        except Exception as e:
            print(f'#1 Error: {e}')
            return False

    return True


if __name__ == '__main__':
    document = Document('samples/playbook_nda.docx')
    create_or_drop_db()
    rs = extract_data_from_playbook(document)
    # for r in rs:
    #     print(len(r[0]))
    #     print(dumps(r[0], indent=4))
    # insert_db(rs[0], rs[1])
