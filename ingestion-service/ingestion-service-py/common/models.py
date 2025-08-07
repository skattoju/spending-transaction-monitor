import datetime
from pydantic import BaseModel
from typing import Optional


from pydantic import Field

class IncomingTransaction(BaseModel):
    User: int
    Card: int
    Year: int
    Month: int
    Day: int
    Time: str
    Amount: str
    use_chip: str = Field(..., alias='Use Chip')
    merchant_name: int = Field(..., alias='Merchant Name')
    merchant_city: str = Field(..., alias='Merchant City')
    merchant_state: Optional[str] = Field(None, alias='Merchant State')
    zip: Optional[str] = Field(None, alias='Zip')
    mcc: int = Field(..., alias='MCC')
    errors: Optional[str] = Field(None, alias='Errors?')
    is_fraud: str = Field(..., alias='Is Fraud?')


class Transaction(BaseModel):
    user: int
    card: int
    year: int
    month: int
    day: int
    time: datetime.time
    amount: float
    use_chip: str
    merchant_id: int
    merchant_city: str
    merchant_state: Optional[str] = None
    zip: Optional[str] = None
    mcc: int
    errors: Optional[str] = None
    is_fraud: bool


class User(BaseModel):
    person: str
    current_age: int
    retirement_age: int
    birth_year: int
    birth_month: int
    gender: str
    address: str
    apartment: Optional[int] = None
    city: str
    state: str
    zipcode: str
    latitude: float
    longitude: float
    per_capita_income_zipcode: str
    yearly_income_person: str
    total_debt: str
    fico_score: int
    num_credit_cards: int


class Card(BaseModel):
    user: int
    card_index: int
    card_brand: str
    card_type: str
    card_number: str
    expires: str
    cvv: int
    has_chip: str
    cards_issued: int
    credit_limit: str
    acct_open_date: str
    year_pin_last_changed: int
    card_on_dark_web: str
