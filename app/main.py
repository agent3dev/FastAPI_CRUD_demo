import models
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from fastapi import FastAPI, Depends, HTTPException, Path
from starlette import status
from database import engine, get_db
from models import Employee, EmployeeRequest, Recipient, RecipientRequest

app = FastAPI()
models.Base.metadata.create_all(bind=engine)
db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/employee")
async def read_all(db: db_dependency):
    return db.query(Employee).all()


@app.get("/employee/{employee_id}", status_code=status.HTTP_200_OK)
async def read_employee(db: db_dependency, employee_id: int = Path(gt=0)):
    employee_model = db.query(Employee).filter(Employee.id == employee_id).first()
    if employee_model is not None:
        return employee_model
    raise HTTPException(status_code=404, detail='Employee not found')


@app.post("/employee", status_code=status.HTTP_201_CREATED)
async def create_employee(db: db_dependency, employee_request: EmployeeRequest):
    employee_model = Employee(**employee_request.model_dump())
    db.add(employee_model)
    db.commit()


@app.put("/employee/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_employee(db: db_dependency,
                          employee_request: EmployeeRequest,
                          employee_id: int = Path(gt=0)):
    employee_model = db.query(Employee).filter(Employee.id == employee_id).first()
    if employee_model is None:
        raise HTTPException(status_code=404, detail='Employee not found')
    employee_model.name = employee_request.name
    employee_model.lastnames = employee_request.lastnames
    employee_model.date_of_birth = employee_request.date_of_birth
    employee_model.employee_number = employee_request.employee_number
    employee_model.CURP = employee_request.CURP
    employee_model.SSN = employee_request.SSN
    employee_model.phone_number = employee_request.phone_number
    employee_model.nationality = employee_request.nationality
    db.add(employee_model)
    db.commit()


@app.delete("/employee/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(db: db_dependency, employee_id: int = Path(gt=0)):
    employee_model = db.query(Employee).filter(Employee.id == employee_id).first()
    if employee_model is None:
        raise HTTPException(status_code=404, detail='Employee not found')
    db.query(Employee).filter(Employee.id == employee_id).delete()
    db.commit()


@app.get("/recipient")
async def read_all(db: db_dependency):
    return db.query(Recipient).all()


@app.post("/recipient", status_code=status.HTTP_201_CREATED)
async def create_recipient(db: db_dependency, recipient_request: RecipientRequest):
    employee_model = db.query(Employee).filter(Employee.id == recipient_request.employee_id).first()
    if employee_model is None:
        raise HTTPException(status_code=404, detail='Employee not found')
    benefit_sum_query = db.query(func.sum(Recipient.benefit_percent)).filter(Recipient.employee_id == employee_model.id)
    benefit_sum = benefit_sum_query.scalar() + recipient_request.benefit_percent
    if benefit_sum > 100:
        raise HTTPException(status_code=409, detail='Benefits would exceed 100 percent')
    recipient_model = Recipient(**recipient_request.model_dump())
    db.add(recipient_model)
    db.commit()


@app.put("/recipient/{recipient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_recipient(db: db_dependency,
                          recipient_request: RecipientRequest,
                          recipient_id: int = Path(gt=0)):
    recipient_model = db.query(Recipient).filter(Recipient.id == recipient_id).first()
    if recipient_model is None:
        raise HTTPException(status_code=404, detail='Recipient not found')
    employee_model = db.query(Employee).filter(Employee.id == recipient_request.employee_id).first()
    if employee_model is None:
        raise HTTPException(status_code=404, detail='Employee not found')
    benefit_sum_query = db.query(func.sum(Recipient.benefit_percent)).filter(Recipient.employee_id == employee_model.id)
    benefit_sum = benefit_sum_query.scalar() + recipient_request.benefit_percent
    if benefit_sum > 100:
        raise HTTPException(status_code=409, detail='Benefits would exceed 100 percent')
    recipient_model.name = recipient_request.name
    recipient_model.lastnames = recipient_request.lastnames
    recipient_model.date_of_birth = recipient_request.date_of_birth
    recipient_model.CURP = recipient_request.CURP
    recipient_model.SSN = recipient_request.SSN
    recipient_model.phone_number = recipient_request.phone_number
    recipient_model.nationality = recipient_request.nationality
    recipient_model.employee_id = recipient_request.employee_id
    db.add(recipient_model)
    db.commit()
