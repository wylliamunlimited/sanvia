from enum import Enum
from datetime import datetime

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
                 first_name: str = "",
                 last_name: str = "",
                 ):
        self.age = age
        self.gender = gender
        self.sex = sex
        self.height = height
        self.weight = weight
        self.conditions = conditions
        self.medications = medications
        self.first_name = first_name
        self.last_name = last_name
    
    @staticmethod
    def from_dict(source):
        try:
            return Survey(
                age=int(source['Age']), 
                gender=source['Gender'], 
                sex=source['Sex'], 
                height=float(source['Height']),
                weight=float(source['Weight']), 
                conditions=source['Conditions'], 
                medications=source['Medications'],
                first_name=source.get('first-name', ''),
                last_name=source.get('last-name', '')
            )
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
            "first-name": self.first_name,
            "last-name": self.last_name
        }
    
    def __repr__(self):
        return (f'Survey(age={self.age}, gender={self.gender}, sex={self.sex}, height={self.height}, weight={self.weight},' 
                f'conditions={self.conditions}, medications={self.medications})')
    
    def contextualize(self):
        f"""Patient Profile:\nAge: {self.age}\nGender: {self.gender}\nSex: {self.sex}\nHeight: {self.height} cm\nWeight: {self.weight} kg\nConditions: {self.conditions}\nMedications: {self.medications}"""
                
                
class WhoopTokenData:
    def __init__(self, 
                 access_token: str,
                 refresh_token: str,
                 scope: str,
                 token_type: str,
                 expires_in: int,
                 expiration_date: datetime,
                 last_updated: datetime):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.scope = scope
        self.token_type = token_type
        self.expires_in = expires_in
        self.expiration_date = expiration_date
        self.last_updated = last_updated

    @staticmethod
    def from_dict(source: dict):
        try:
            return WhoopTokenData(
                access_token=source['access_token'],
                refresh_token=source['refresh_token'],
                scope=source['scope'],
                token_type=source['token_type'],
                expires_in=int(source['expires_in']),
                expiration_date=datetime.fromisoformat(source['expiration_date']),
                last_updated=datetime.fromisoformat(source['last_updated']),
            )
        except KeyError as e:
            raise ValueError(f"Missing key in source data: {e}")
        except Exception as e:
            raise ValueError(f"Invalid token data: {e}")

    def to_dict(self):
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "scope": self.scope,
            "token_type": self.token_type,
            "expires_in": self.expires_in,
            "expiration_date": self.expiration_date.isoformat(),
            "last_updated": self.last_updated.isoformat(),
        }

    def __repr__(self):
        return (f"WhoopTokenData(access_token='{self.access_token[:10]}...', refresh_token='{self.refresh_token[:10]}...', "
                f"scope='{self.scope}', token_type='{self.token_type}', expires_in={self.expires_in}, "
                f"expiration_date='{self.expiration_date}', last_updated='{self.last_updated}')")
                
class EPICTokenData:
    def __init__(self, 
                 patient: str,
                 access_token: str,
                 scope: str,
                 token_type: str,
                 expires_in: int,
                 expiration_date: datetime,
                 last_updated: datetime):
        self.patient = patient
        self.access_token = access_token
        self.scope = scope
        self.token_type = token_type
        self.expires_in = expires_in
        self.expiration_date = expiration_date
        self.last_updated = last_updated

    @staticmethod
    def from_dict(source: dict):
        try:
            return EPICTokenData(
                patient=source["patient"],
                access_token=source['access_token'],
                scope=source['scope'],
                token_type=source['token_type'],
                expires_in=int(source['expires_in']),
                expiration_date=datetime.fromisoformat(source['expiration_date']),
                last_updated=datetime.fromisoformat(source['last_updated']),
            )
        except KeyError as e:
            raise ValueError(f"Missing key in source data: {e}")
        except Exception as e:
            raise ValueError(f"Invalid token data: {e}")

    def to_dict(self):
        return {
            "patient": self.patient,
            "access_token": self.access_token,
            "scope": self.scope,
            "token_type": self.token_type,
            "expires_in": self.expires_in,
            "expiration_date": self.expiration_date.isoformat(),
            "last_updated": self.last_updated.isoformat(),
        }

    def __repr__(self):
        return (f"EPICTokenData(patient='{self.patient[:10]}...', access_token='{self.access_token[:10]}...', "
                f"scope='{self.scope}', token_type='{self.token_type}', expires_in={self.expires_in}, "
                f"expiration_date='{self.expiration_date}', last_updated='{self.last_updated}')")