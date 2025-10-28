from pydantic import BaseModel, ConfigDict

class BranchResponse(BaseModel):
    id: int
    name: str
    location: str

    model_config = ConfigDict(from_attributes=True)