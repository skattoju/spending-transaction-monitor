from enum import Enum

from pydantic import BaseModel, Field


class TransactionType(str, Enum):
    PURCHASE = 'PURCHASE'
    REFUND = 'REFUND'
    CASHBACK = 'CASHBACK'
    FEE = 'FEE'
    INTEREST = 'INTEREST'
    PAYMENT = 'PAYMENT'


class TransactionStatus(str, Enum):
    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    DECLINED = 'DECLINED'
    CANCELLED = 'CANCELLED'
    SETTLED = 'SETTLED'


# Transaction Schemas
class TransactionBase(BaseModel):
    amount: float = Field(..., description='Transaction amount', gt=0)
    currency: str = Field('USD', description='Transaction currency')
    description: str = Field(..., description='Transaction description')
    merchant_name: str = Field(..., description='Merchant name')
    merchant_category: str = Field(..., description='Merchant category')
    transaction_date: str = Field(
        ..., description="Transaction date in ISO format (e.g., '2024-01-16T14:45:00Z')"
    )
    transaction_type: TransactionType = Field(
        TransactionType.PURCHASE, description='Type of transaction'
    )
    merchant_city: str | None = Field(None, description='Merchant city')
    merchant_state: str | None = Field(None, description='Merchant state')
    merchant_country: str | None = Field(None, description='Merchant country')
    merchant_zipcode: str | None = Field(None, description='Merchant zipcode')
    merchant_latitude: float | None = Field(None, description='Merchant latitude')
    merchant_longitude: float | None = Field(None, description='Merchant longitude')
    status: TransactionStatus = Field(
        TransactionStatus.PENDING, description='Transaction status'
    )
    authorization_code: str | None = Field(None, description='Authorization code')
    trans_num: str | None = Field(None, description='Reference number')


class TransactionCreate(TransactionBase):
    id: str = Field(..., description='Transaction ID')
    user_id: str = Field(..., description='User ID')
    credit_card_num: str = Field(..., description='Credit card ID')


class TransactionUpdate(BaseModel):
    amount: float | None = Field(None, description='Transaction amount', gt=0)
    currency: str | None = Field(None, description='Transaction currency')
    description: str | None = Field(None, description='Transaction description')
    merchant_name: str | None = Field(None, description='Merchant name')
    merchant_category: str | None = Field(None, description='Merchant category')
    transaction_date: str | None = Field(
        None, description='Transaction date in ISO format'
    )
    transaction_type: TransactionType | None = Field(
        None, description='Type of transaction'
    )
    merchant_city: str | None = Field(None, description='Merchant city')
    merchant_state: str | None = Field(None, description='Merchant state')
    merchant_country: str | None = Field(None, description='Merchant country')
    merchant_zipcode: str | None = Field(None, description='Merchant zipcode')
    merchant_latitude: float | None = Field(None, description='Merchant latitude')
    merchant_longitude: float | None = Field(None, description='Merchant longitude')
    status: TransactionStatus | None = Field(None, description='Transaction status')
    authorization_code: str | None = Field(None, description='Authorization code')
    trans_num: str | None = Field(None, description='Reference number')


class TransactionOut(TransactionBase):
    id: str
    user_id: str
    credit_card_num: str
    created_at: str
    updated_at: str


# Credit Card Schemas
class CreditCardBase(BaseModel):
    card_number: str = Field(..., description='Card number (last 4 digits)')
    card_type: str = Field(..., description='Card type (Visa, Mastercard, etc.)')
    bank_name: str = Field(..., description='Bank name')
    card_holder_name: str = Field(..., description='Card holder name')
    expiry_month: int = Field(..., description='Expiry month (1-12)', ge=1, le=12)
    expiry_year: int = Field(..., description='Expiry year', ge=2024)
    is_active: bool = Field(True, description='Whether the card is active')


class CreditCardCreate(CreditCardBase):
    user_id: str = Field(..., description='User ID')


class CreditCardUpdate(BaseModel):
    card_number: str | None = Field(None, description='Card number (last 4 digits)')
    card_type: str | None = Field(
        None, description='Card type (Visa, Mastercard, etc.)'
    )
    bank_name: str | None = Field(None, description='Bank name')
    card_holder_name: str | None = Field(None, description='Card holder name')
    expiry_month: int | None = Field(
        None, description='Expiry month (1-12)', ge=1, le=12
    )
    expiry_year: int | None = Field(None, description='Expiry year', ge=2024)
    is_active: bool | None = Field(None, description='Whether the card is active')


class CreditCardOut(CreditCardBase):
    id: str
    user_id: str
    created_at: str
    updated_at: str


# Transaction Summary Schemas
class TransactionSummary(BaseModel):
    totalTransactions: int = Field(..., description='Total number of transactions')
    totalAmount: float = Field(..., description='Total transaction amount')
    averageAmount: float = Field(..., description='Average transaction amount')
    largestTransaction: float = Field(..., description='Largest transaction amount')
    smallestTransaction: float = Field(..., description='Smallest transaction amount')


class CategorySpending(BaseModel):
    category: str = Field(..., description='Merchant category')
    totalAmount: float = Field(..., description='Total spending in this category')
    transactionCount: int = Field(
        ..., description='Number of transactions in this category'
    )
    averageAmount: float = Field(
        ..., description='Average transaction amount in this category'
    )


class SpendingAnalysis(BaseModel):
    user_id: str = Field(..., description='User ID')
    period: str = Field(..., description="Analysis period (e.g., 'last_30_days')")
    summary: TransactionSummary = Field(..., description='Transaction summary')
    categoryBreakdown: list[CategorySpending] = Field(
        ..., description='Spending by category'
    )
    topMerchants: list[dict] = Field(..., description='Top merchants by spending')
    recentTransactions: list[TransactionOut] = Field(
        ..., description='Recent transactions'
    )


# Transaction Filter Schemas
class TransactionFilters(BaseModel):
    user_id: str | None = Field(None, description='Filter by user ID')
    credit_card_num: str | None = Field(None, description='Filter by credit card ID')
    merchant_category: str | None = Field(
        None, description='Filter by merchant category'
    )
    merchant_name: str | None = Field(None, description='Filter by merchant name')
    transaction_type: TransactionType | None = Field(
        None, description='Filter by transaction type'
    )
    status: TransactionStatus | None = Field(
        None, description='Filter by transaction status'
    )
    minAmount: float | None = Field(None, description='Minimum transaction amount')
    maxAmount: float | None = Field(None, description='Maximum transaction amount')
    startDate: str | None = Field(None, description='Start date in ISO format')
    endDate: str | None = Field(None, description='End date in ISO format')
    location: str | None = Field(None, description='Filter by location')


# Transaction Import Schemas
class TransactionImport(BaseModel):
    transactions: list[TransactionCreate] = Field(
        ..., description='List of transactions to import'
    )
    source: str = Field(..., description="Import source (e.g., 'csv', 'api', 'manual')")
    importDate: str = Field(..., description='Import date in ISO format')


class ImportResult(BaseModel):
    totalProcessed: int = Field(..., description='Total transactions processed')
    successful: int = Field(..., description='Number of successful imports')
    failed: int = Field(..., description='Number of failed imports')
    errors: list[str] = Field(..., description='List of error messages')


# Transaction Export Schemas
class ExportFormat(str, Enum):
    CSV = 'csv'
    JSON = 'json'
    PDF = 'pdf'
    EXCEL = 'excel'


class TransactionExport(BaseModel):
    user_id: str = Field(..., description='User ID')
    format: ExportFormat = Field(ExportFormat.CSV, description='Export format')
    filters: TransactionFilters | None = Field(None, description='Export filters')
    includeSummary: bool = Field(True, description='Include summary in export')


# Transaction Statistics Schemas
class DailySpending(BaseModel):
    date: str = Field(..., description='Date in YYYY-MM-DD format')
    totalAmount: float = Field(..., description='Total spending for the day')
    transactionCount: int = Field(..., description='Number of transactions for the day')


class MonthlySpending(BaseModel):
    year: int = Field(..., description='Year')
    month: int = Field(..., description='Month (1-12)')
    totalAmount: float = Field(..., description='Total spending for the month')
    transactionCount: int = Field(
        ..., description='Number of transactions for the month'
    )
    averageDailySpending: float = Field(..., description='Average daily spending')
    topCategories: list[CategorySpending] = Field(
        ..., description='Top spending categories'
    )


class SpendingTrends(BaseModel):
    user_id: str = Field(..., description='User ID')
    period: str = Field(..., description='Analysis period')
    dailySpending: list[DailySpending] = Field(..., description='Daily spending data')
    monthlySpending: list[MonthlySpending] = Field(
        ..., description='Monthly spending data'
    )
    spendingGrowth: float = Field(..., description='Spending growth percentage')
    categoryTrends: list[CategorySpending] = Field(
        ..., description='Category spending trends'
    )
