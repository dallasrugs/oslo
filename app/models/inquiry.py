from pydantic import BaseModel

class Inquiry(BaseModel):
    subject: str
    email: str
    contact_name: str
    phone: str = None
    message: str = None
    city: str = None
