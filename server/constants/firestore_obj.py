from enum import Enum

class Gender(Enum):
    Men = "Men"
    Women = "Women"
    Nonbinary = "Nonbinary"
    
class Sex(Enum):
    Male = "Male"
    Female = "Female"
    Intersex = "Intersex"

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
            return Survey(age=int(source['Age']), gender=source['Gender'], sex=source['Sex'], height=float(source['Height']), weight=float(source['Weight']))
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