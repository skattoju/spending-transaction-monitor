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
    merchantName: str = Field(..., description='Merchant name')
    merchantCategory: str = Field(..., description='Merchant category')
    transactionDate: str = Field(
        ..., description="Transaction date in ISO format (e.g., '2024-01-16T14:45:00Z')"
    )
    transactionType: TransactionType = Field(
        TransactionType.PURCHASE, description='Type of transaction'
    )
    merchantLocation: str | None = Field(None, description='Merchant location')
    merchantCity: str | None = Field(None, description='Merchant city')
    merchantState: str | None = Field(None, description='Merchant state')
    merchantCountry: str | None = Field(None, description='Merchant country')
    status: TransactionStatus = Field(
        TransactionStatus.PENDING, description='Transaction status'
    )
    authorizationCode: str | None = Field(None, description='Authorization code')
    referenceNumber: str | None = Field(None, description='Reference number')


class TransactionCreate(TransactionBase):
    id: str = Field(..., description='Transaction ID')
    userId: str = Field(..., description='User ID')
    creditCardId: str = Field(..., description='Credit card ID')


class TransactionUpdate(BaseModel):
    amount: float | None = Field(None, description='Transaction amount', gt=0)
    currency: str | None = Field(None, description='Transaction currency')
    description: str | None = Field(None, description='Transaction description')
    merchantName: str | None = Field(None, description='Merchant name')
    merchantCategory: str | None = Field(None, description='Merchant category')
    transactionDate: str | None = Field(
        None, description='Transaction date in ISO format'
    )
    transactionType: TransactionType | None = Field(
        None, description='Type of transaction'
    )
    merchantLocation: str | None = Field(None, description='Merchant location')
    merchantCity: str | None = Field(None, description='Merchant city')
    merchantState: str | None = Field(None, description='Merchant state')
    merchantCountry: str | None = Field(None, description='Merchant country')
    status: TransactionStatus | None = Field(None, description='Transaction status')
    authorizationCode: str | None = Field(None, description='Authorization code')
    referenceNumber: str | None = Field(None, description='Reference number')


class TransactionOut(TransactionBase):
    id: str
    userId: str
    creditCardId: str
    createdAt: str
    updatedAt: str


# Credit Card Schemas
class CreditCardBase(BaseModel):
    cardNumber: str = Field(..., description='Card number (last 4 digits)')
    cardType: str = Field(..., description='Card type (Visa, Mastercard, etc.)')
    bankName: str = Field(..., description='Bank name')
    cardHolderName: str = Field(..., description='Card holder name')
    expiryMonth: int = Field(..., description='Expiry month (1-12)', ge=1, le=12)
    expiryYear: int = Field(..., description='Expiry year', ge=2024)
    isActive: bool = Field(True, description='Whether the card is active')


class CreditCardCreate(CreditCardBase):
    userId: str = Field(..., description='User ID')


class CreditCardUpdate(BaseModel):
    cardNumber: str | None = Field(None, description='Card number (last 4 digits)')
    cardType: str | None = Field(None, description='Card type (Visa, Mastercard, etc.)')
    bankName: str | None = Field(None, description='Bank name')
    cardHolderName: str | None = Field(None, description='Card holder name')
    expiryMonth: int | None = Field(
        None, description='Expiry month (1-12)', ge=1, le=12
    )
    expiryYear: int | None = Field(None, description='Expiry year', ge=2024)
    isActive: bool | None = Field(None, description='Whether the card is active')


class CreditCardOut(CreditCardBase):
    id: str
    userId: str
    createdAt: str
    updatedAt: str


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
    userId: str = Field(..., description='User ID')
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
    userId: str | None = Field(None, description='Filter by user ID')
    creditCardId: str | None = Field(None, description='Filter by credit card ID')
    merchantCategory: str | None = Field(
        None, description='Filter by merchant category'
    )
    merchantName: str | None = Field(None, description='Filter by merchant name')
    transactionType: TransactionType | None = Field(
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
    userId: str = Field(..., description='User ID')
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
    userId: str = Field(..., description='User ID')
    period: str = Field(..., description='Analysis period')
    dailySpending: list[DailySpending] = Field(..., description='Daily spending data')
    monthlySpending: list[MonthlySpending] = Field(
        ..., description='Monthly spending data'
    )
    spendingGrowth: float = Field(..., description='Spending growth percentage')
    categoryTrends: list[CategorySpending] = Field(
        ..., description='Category spending trends'
    )
