from pydantic import BaseModel


class UserOut(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    phone_number: str | None = None
    is_active: bool
    created_at: str | None = None
    updated_at: str | None = None
    credit_cards_count: int
    transactions_count: int
