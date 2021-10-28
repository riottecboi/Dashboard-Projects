from sqlalchemy import Column, Integer, String, SmallInteger, ForeignKey, DateTime, Boolean, UniqueConstraint, Text, UnicodeText
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from os import urandom
from binascii import hexlify
from hashlib import sha512
from datetime import datetime
import pytz

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    username = Column(String(255), primary_key=True)
    password = Column(String(255))
    password_salt = Column(String(255))
    authenticated = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)

    def is_active(self):
        return True

    def is_authenticated(self):
        return self.authenticated

    def set_authenticated(self, session, value):
        self.authenticated = value
        session.add(self)
        session.commit()

    def get_id(self):
        return self.username

    def generate_salt(self):
        self.password_salt = hexlify(urandom(32)).decode('utf-8').upper()
        return self.password_salt

    def change_password(self, password):
        self.generate_salt()
        self.password = self.generate_password_hash(password, self.password_salt)
        return

    def generate_password_hash(self, password, salt):
        return sha512(salt.encode('utf-8') + password.encode('utf-8')).hexdigest().upper()

    def check_password(self, password):
        hash = self.generate_password_hash(password, self.password_salt)
        if hash == self.password:
            return True
        return False


class Customer(Base):
    __tablename__ = 'customers'
    ######### CUSTOMER'S PART ##########
    id = Column(Integer, primary_key=True, autoincrement=True)
    timereported = Column(DateTime, default=datetime.now(pytz.timezone('Asia/Bangkok')))
    name = Column(String(128,convert_unicode=True,collation='utf8mb4_general_ci'), nullable=False)
    dob = Column(String(16,convert_unicode=True))
    phone = Column(Integer, nullable=False, unique=True)
    status = Column(String(32, convert_unicode=True, collation='utf8mb4_general_ci'), nullable=False)
    is_display = Column(SmallInteger,default=1)
    # rev = Column(Text(convert_unicode=True), nullable=False)#right eye vision
    # lev = Column(Text(convert_unicode=True), nullable=False)#left eye vision
    # distance = Column(String(64,convert_unicode=True,collation='utf8mb4_general_ci'))#(far, close, both)
    # frev = Column(Text(convert_unicode=True), nullable=False)#far right eye vision
    # flev = Column(Text(convert_unicode=True), nullable=False)#far left eye vision
    # frevo = Column(Text(convert_unicode=True), nullable=False)#far right eye vision optics
    # flevo = Column(Text(convert_unicode=True), nullable=False)#far left eye vision optics
    # crevo = Column(Text(convert_unicode=True), nullable=False)#close right eye vision optics
    # clevo = Column(Text(convert_unicode=True), nullable=False)#close left eye vision optics
    # pd = Column(Text(convert_unicode=True), nullable=False)#pupil distance
    # lens = Column(String(128,convert_unicode=True,collation='utf8mb4_general_ci'))#lens brand name
    # ######### DIAGNOSE ##########
    # dre = Column(String(128,convert_unicode=True,collation='utf8mb4_general_ci'))#diagnose right eye
    # dle = Column(String(128,convert_unicode=True,collation='utf8mb4_general_ci'))#diagnose left eye
    # ######### DRUG'S PART #############
    # drug_name = Column(String(128,convert_unicode=True,collation='utf8mb4_general_ci'))
    # day_per_times = Column(Integer)
    # quantity_per_times = Column(Integer)
    # method = Column(String(16,convert_unicode=True,collation='utf8mb4_general_ci'))
    # eyes = Column(String(16,convert_unicode=True,collation='utf8mb4_general_ci'))
    # use_when = Column(String(32,convert_unicode=True,collation='utf8mb4_general_ci'))
    # quantity = Column(Integer)
    # unit = Column(String(32,convert_unicode=True,collation='utf8mb4_general_ci'))
    # note = Column(Text(convert_unicode=True,collation='utf8mb4_general_ci'))

class Record(Base):
    __tablename__ = 'records'
    id = Column(Integer, primary_key=True, autoincrement=True)
    customerid = Column(Integer, ForeignKey('customers.id'), nullable=False)
    jsondata = Column(Text(4294000000,convert_unicode=True,collation='utf8mb4_general_ci'))
    date_updated = Column(DateTime, default=datetime.now(pytz.timezone('Asia/Bangkok')))
