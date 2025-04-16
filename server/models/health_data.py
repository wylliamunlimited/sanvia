from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class SleepStage(BaseModel):
    type: str
    start_time: datetime
    end_time: datetime


class SleepData(BaseModel):
    start_time: datetime
    end_time: datetime
    stages: List[SleepStage]


class StepData(BaseModel):
    count: int
    start_time: datetime
    end_time: datetime


class HeartRateData(BaseModel):
    rate: float
    timestamp: datetime


class WeightData(BaseModel):
    weight: float
    timestamp: datetime


class HealthData(BaseModel):
    user_id: str
    device_id: str
    timestamp: datetime
    steps: List[StepData]
    heart_rate: List[HeartRateData]
    sleep: List[SleepData]
    weight: List[WeightData]
