from pydantic import BaseModel, Field

class PreVisitSummary(BaseModel):
    urgency_level: str = Field(..., description="High, Medium, or Low based on symptoms")
    chief_complaint: str = Field(..., description="A clear, concise summary of the patient's symptoms")
    suggested_questions: list[str] = Field(..., description="3-5 suggested diagnostic questions for the doctor to ask")

class PostVisitSummary(BaseModel):
    patient_summary: str = Field(..., description="A clear, friendly summary of the diagnosis and next steps for the patient to read")
    medication_schedule: list[str] = Field(..., description="A simple list of medications and when to take them")
    follow_up_instructions: str = Field(..., description="When the patient should follow up or seek emergency care")
