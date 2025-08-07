export interface IncomingTransaction {
    User: number;
    Card: number;
    Year: number;
    Month: number;
    Day: number;
    Time: string;
    Amount: string;
    "Use Chip": string;
    "Merchant Name": number;
    "Merchant City": string;
    "Merchant State"?: string;
    "Zip"?: string;
    MCC: number;
    "Errors?"?: string;
    "Is Fraud?": string;
}

export interface Transaction {
    user: number;
    card: number;
    year: number;
    month: number;
    day: number;
    time: string;
    amount: number;
    use_chip: string;
    merchant_id: number;
    merchant_city: string;
    merchant_state?: string;
    zip?: string;
    mcc: number;
    errors?: string;
    is_fraud: boolean;
}

export interface User {
    person: string;
    current_age: number;
    retirement_age: number;
    birth_year: number;
    birth_month: number;
    gender: string;
    address: string;
    apartment?: number;
    city: string;
    state: string;
    zipcode: string;
    latitude: number;
    longitude: number;
    per_capita_income_zipcode: string;
    yearly_income_person: string;
    total_debt: string;
    fico_score: number;
    num_credit_cards: number;
}

export interface Card {
    user: number;
    card_index: number;
    card_brand: string;
    card_type: string;
    card_number: string;
    expires: string;
    cvv: number;
    has_chip: string;
    cards_issued: number;
    credit_limit: string;
    acct_open_date: string;
    year_pin_last_changed: number;
    card_on_dark_web: string;
}
