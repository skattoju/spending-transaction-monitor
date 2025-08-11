from pydantic import BaseModel


class UserOut(BaseModel):
    id: str
    email: str
    firstName: str
    lastName: str
    phoneNumber: str | None = None
    isActive: bool
    createdAt: str | None = None
    updatedAt: str | None = None
    creditCardsCount: int
    transactionsCount: int


