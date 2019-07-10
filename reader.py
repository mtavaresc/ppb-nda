from docx import Document
from docx.shared import Pt
from json import dumps
from re import findall, sub, match
from itertools import groupby
from base import Base, Session, engine
from models import Issues, CustomersRequest, Fallback
from sqlalchemy.exc import IntegrityError

Base.metadata.create_all(engine)

doc = Document('samples/playbook_nda.docx')
data_list = []
issues_a = []
issues_b = []
issue_id = ''
# issue_text = ''
# customers_request = []
# principles = ''
# sample_language = ''
# fallback_list = []
# fallback_id = ''
# fallback_approval = ''

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
        tup = issues_a[-1] + (cr_dict,)
        issues_a.pop()
        issues_a.append(tup)
        # print(tup)
    # for run in paragraph.runs:
    #     if run.bold and ':' in paragraph.text:
    # if paragraph.text.split(':')[1].strip() != '':

    # fullText.append(para.text)
    # return '\n'.join(fullText)

s = Session()

a = issues_a
b = issues_b
for j in list(a for a, _ in groupby(a)):
    print(j)
    try:
        s.merge(Issues(issue=j[0], name=j[1]))
        s.add(CustomersRequest(issue=j[0], idx=j[2]['id'], customer_request=j[2]['customer_request'], principles=''))
        s.commit()
    except IntegrityError:
        s.rollback()
    except IndexError:
        for k in list(b for b, _ in groupby(b)):
            if j[0] == findall(r'\d+', k[0])[0]:
                s.add(CustomersRequest(issue=j[0], idx=k[0][-1:], customer_request=k[1], principles=''))
                try:
                    s.commit()
                except IntegrityError:
                    s.rollback()
                except Exception as e:
                    print(f'#2 Error: {e}')
    except Exception as e:
        print(f'#1 Error: {e}')
#         else:
#             pass
#             # s.add(CustomersRequest(issue=j[0], idx='A', customer_request=k[1], principles=''))
#             # s.commit()
#
