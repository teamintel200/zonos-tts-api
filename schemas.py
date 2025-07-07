from pydantic import BaseModel
from typing import List

class Segment(BaseModel):
    id: int
    text: str

class TTSRequest(BaseModel):
    segments: List[Segment]
    tempdir: str

class CombineRequest(BaseModel):
    tempdir: str
