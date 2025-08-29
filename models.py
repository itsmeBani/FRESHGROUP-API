# models.py
from pydantic import BaseModel

class StudentInterface(BaseModel):
    ID: str
    Lastname: str
    Firstname: str
    FamilyIncome: int
    TypeofSeniorHighSchool: str
    ProgramEnrolled: str
    MunicipalityOfOrigin: str
    Grade12GWA: float
    Sex: str
