from pydantic import BaseModel, Field
from typing import List

class ServiceTicket(BaseModel):
    citizen_language_detected: str = Field(description="The primary language or mixture of dialects detected in the audio or text input.")
    english_translation: str = Field(description="Accurate, coherent translation of the citizen's complaint into professional English.")
    category: str = Field(description="Must map strictly to one of: 'water_sanitation', 'electricity_power', 'roads_stormwater', 'refuse_waste', 'housing', 'other'.")
    severity: str = Field(description="Priority rating based on public hazard: 'critical', 'high', 'medium', 'low'.")
    location_clues: List[str] = Field(description="Extracted local landmarks, street names, suburbs, or wards mentioned to identify the location.")
    key_entities: List[str] = Field(description="Specific items damaged or failing (e.g., 'substation', 'pothole', 'burst main pipe').")
    batho_pele_justification: str = Field(description="A brief explanation of how addressing this ticket fulfills the 'People First' mandate.")
