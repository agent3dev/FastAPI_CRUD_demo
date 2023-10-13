import re
from datetime import date
from database import Base, get_db
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from pydantic import BaseModel, Field, validator


class Employee(Base):
    __tablename__ = 'employee'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    lastnames = Column(String(255))
    date_of_birth = Column(Date)
    employee_number = Column(Integer)
    CURP = Column(String(25))
    SSN = Column(String(25))
    phone_number = Column(String(10))
    nationality = Column(String(25))
    recipients = relationship("Recipient", cascade="all, delete")


class EmployeeRequest(BaseModel):
    name: str = Field(min_length=3)
    lastnames: str = Field(min_length=10)
    employee_number: int = Field(gt=0)
    CURP: str = Field(min_length=18)
    SSN: str = Field(min_length=10)
    date_of_birth: date = None
    phone_number: str = Field(min_length=10)
    nationality: str = Field(min_length=5)

    @validator("phone_number")
    def phone_validate(cls, value):
        if not value:
            return None
        if re.match(r"^\d{10}$", value):
            return value
        raise ValueError("The 'phone' parameter is not a valid phone number")

    @validator('date_of_birth')
    def validate_age(cls, date_of_birth):
        today = date.today()
        age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
        if age < 18:
            raise ValueError("Person must be over 18 years old.")
        return date_of_birth


class Recipient(Base):
    __tablename__ = 'recipient'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    lastnames = Column(String(255))
    date_of_birth = Column(Date)
    CURP = Column(String(25))
    SSN = Column(String(25))
    phone_number = Column(String(10))
    nationality = Column(String(25))
    benefit_percent = Column(Integer)
    employee_id = Column(Integer, ForeignKey('employee.id', ondelete='CASCADE'))


class RecipientRequest(BaseModel):
    name: str = Field(min_length=3)
    lastnames: str = Field(min_length=10)
    employee_id: int = Field(gt=0)
    CURP: str = Field(min_length=18)
    SSN: str = Field(min_length=10)
    date_of_birth: date = None
    phone_number: str = Field(min_length=10)
    nationality: str = Field(min_length=5)
    benefit_percent: int = Field(lt=101)

    @validator("phone_number")
    def phone_validate(cls, value):
        if not value:
            return None
        if re.match(r"^\d{10}$", value):
            return value
        raise ValueError("The 'phone' parameter is not a valid phone number")

    @validator('date_of_birth')
    def validate_age(cls, date_of_birth):
        today = date.today()
        age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
        if age < 18:
            raise ValueError("Person must be over 18 years old.")
        return date_of_birth