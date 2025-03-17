from enum import Enum

class Gender(Enum):
    Men = 1
    Women = 2
    Nonbinary = 3
    
class Sex(Enum):
    Male = 1
    Female = 2
    Intersex = 3

# FIRESTORE DATA OBJECTS

class Survey:
    def __init__(self, 
                 age: int,
                 gender: Gender,
                 sex: Sex,
                 height: float, ## in cm
                 weight: float ## in kg
                 ):
        self.age = age
        self.gender = gender
        self.sex = sex
        self.height = height
        self.weight = weight
    
    @staticmethod
    def from_dict(source):
        try:
            return Survey(age=source['Age'], gender=source['Gender'], sex=source['Sex'], height=source['Height'], weight=source['Weight'])
        except Exception as e:
            raise ValueError("Make sure all the fields are entered: age, gender, sex, height, weight")
    
    def to_dict(self):
        return {
            "Age": self.age,
            "Gender": self.gender,
            "Sex": self.sex,
            "Height": self.height,
            "Weight": self.weight
        }
    
    def __repr__(self):
        return f'Survey(age={self.age}, gender={self.gender}, sex={self.sex}, height={self.height}, weight={self.weight}'