from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, DateTime, Boolean, UniqueConstraint, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from os import urandom
from binascii import hexlify
from hashlib import sha512

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    username = Column(String(255), primary_key=True)
    password = Column(String(255))
    password_salt = Column(String(255))
    is_admin = Column(Boolean, default=False)

    def is_active(self):
        return True

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
    __tablename__ = 'customer'
    ######### CUSTOMER'S PART ##########
    id = Column(Integer, primary_key=True, autoincrement=True)
    timereported = Column(TIMESTAMP)
    name = Column(String(128), nullable=False)
    dob = Column(String(16))
    phone = Column(Integer, nullable=False)
    rev = Column(Text, nullable=False)#right eye vision
    lev = Column(Text, nullable=False)#left eye vision
    distance = Column(String(64))#(far, close, both)
    frev = Column(Text, nullable=False)#far right eye vision
    flev = Column(Text, nullable=False)#far left eye vision
    frevo = Column(Text, nullable=False)#far right eye vision optics
    flevo = Column(Text, nullable=False)#far left eye vision optics
    crevo = Column(Text, nullable=False)#close right eye vision optics
    clevo = Column(Text, nullable=False)#close left eye vision optics
    pd = Column(Text, nullable=False)#pupil distance
    lens = Column(String(128))#lens brand name
    ######### DRUG'S PART #############
    drug_name = Column(String(128))
    times = Column(Integer)
    methods = Column(String(16))
    eyes = Column(String(16))
    use_when = Column(String(32))
    quantity = Column(Integer)
    unit = Column(String(32))
    note = Column(Text)

