from pydantic import (
    BaseModel,
    ConfigDict,
    StrictBool,
    StrictStr,
)


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: StrictStr | None = None


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: StrictStr | None = None
    done: StrictBool | None = None


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    done: bool