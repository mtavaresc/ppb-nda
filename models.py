from base import Base
from sqlalchemy import Column, String, Text, ForeignKey, Integer, CHAR, PrimaryKeyConstraint
from sqlalchemy.orm import relationship


class Issues(Base):
    __tablename__ = 'issues'

    issue = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(255), nullable=False)

    requests = relationship('CustomersRequest', cascade='all, delete-orphan')
    fallback = relationship('Fallback', cascade='all, delete-orphan')

    def __init__(self, issue, name):
        self.issue = issue
        self.name = name

    def __repr__(self):
        return f'<Issue #{self.issue}>'


class CustomersRequest(Base):
    __tablename__ = 'customers_request'

    issue = Column(Integer, ForeignKey('issues.issue'), nullable=False)
    id = Column(CHAR(1), nullable=False)
    customer_request = Column(String(255), nullable=False)
    principles = Column(Text, nullable=False)
    PrimaryKeyConstraint(id, issue, name='pk_customers_request')

    fallback = relationship('Fallback', cascade='all, delete-orphan')

    def __init__(self, issue, idx, customer_request, principles):
        self.issue = issue
        self.id = idx
        self.customer_request = customer_request
        self.principles = principles

    def __repr__(self):
        return f'<Customer Request {self.id}>'


class Fallback(Base):
    __tablename__ = 'fallback'

    """ For Category use: Sample Language, Dell EMC Standard Language and Fallback """
    category = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    approval = Column(Text, nullable=True)
    issue = Column(Integer, ForeignKey('issues.issue'), nullable=False)
    request = Column(CHAR(1), ForeignKey('customers_request.id'), nullable=False)
    content_hash = Column(String(32), primary_key=True)

    def __init__(self, category, content, approval, issue, request, content_hash):
        self.category = category
        self.content = content
        self.approval = approval
        self.issue = issue
        self.request = request
        self.content_hash = content_hash

    def __repr__(self):
        return f'<Fallback #{self.content_hash}>'
