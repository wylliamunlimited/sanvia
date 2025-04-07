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
                 weight: float, ## in kg
                 conditions: list = [],
                 medications: list = [],
                 ):
        self.age = age
        self.gender = gender
        self.sex = sex
        self.height = height
        self.weight = weight
        self.conditions = conditions
        self.medications = medications
        self.onboarding = "complete"
    
    @staticmethod
    def from_dict(source):
        try:
            return Survey(age=int(source['Age']), gender=source['Gender'], sex=source['Sex'], height=float(source['Height']),
                          weight=float(source['Weight'], conditions=source['Conditions'], medications=source['Medications']),)
        except Exception as e:
            raise ValueError("Make sure all the fields are entered: age, gender, sex, height, weight, conditions, medications.")
    
    def to_dict(self):
        return {
            "Age": self.age,
            "Gender": self.gender,
            "Sex": self.sex,
            "Height": self.height,
            "Weight": self.weight,
            "Conditions": self.conditions,
            "Medications": self.medications,
            "onboarding": self.onboarding
        }
    
    def __repr__(self):
        return (f'Survey(age={self.age}, gender={self.gender}, sex={self.sex}, height={self.height}, weight={self.weight},' 
                f'conditions={self.conditions}, medications={self.medications}, onboarding={self.onboarding})')
    
    def contextualize(self):
        f"""Patient Profile:
                Age: {self.age}
                Gender: {self.gender}
                Sex: {self.sex}
                Height: {self.height} cm
                Weight: {self.weight} kg"""