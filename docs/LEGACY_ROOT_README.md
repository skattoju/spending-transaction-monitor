# Spending Transaction Monitor Architecture, Technology, & Testing Overview

This document outlines a high-level architecture for an **AI-driven Spending Transaction Monitor** for credit card transactions, addressing the sophisticated natural language alerting requirements and user stories provided.
It details the runtime data flow, the monorepo file structure, the specific technology stack for each component, and the comprehensive testing strategy.

## High-Level Overview

The system will act as an intelligent intermediary between credit card transaction streams and the customer. It will ingest real-time transaction data, process user-defined natural language alert rules using AI, evaluate transactions against these rules, and trigger notifications when criteria are met.

## Architectural Diagram

This diagram shows the event-driven flow of a transaction from ingestion to the final email notification.

```mermaid
graph TD
    subgraph "User"
      M[User]
    end
    subgraph "External System"
        A[Transaction Source]
        M --> |Completes Credit Card Transaction| A;
    end

    subgraph "OpenShift Cluster"
        subgraph "Ingestion & Buffering"
            B(Ingestion Service);
            C(Kafka Topic: 'raw-transactions');
            A -->|HTTP| B;
            B -->|Publishes| C;
        end

        subgraph "Application"
            J("Online Banking Customer UI")
            K(LlamaStack Service);
            M --> |Creates Rules| J;
            J -->|NLP| K;
        end

        subgraph "Openshift AI"
            L(LLM Service);
            K -->|Inferencing| L;
            
        end

        subgraph "Business Logic & Rules"
            N(NLP MCP Agent);
            D(Rules Engine / Alerting Service);
            E(Historical DB);
            O(Alert Rules DB);
            P("Location Services Integration");
            Q(AI/ML Behavioral Analysis);
            R("User DB");
            C -->|Consumes raw event| D;
            D <-->|Queries for context| E;
            K --> |Creates Rules| N;
            N --> |Store Rules| O;
            D --> |Access User Data| R;
            D --> |Access Rules Data| O;
            D --> |Behavior Analysis| Q;
            D --> |Fetch User Location| P; 
            Q --> |Access Transaction Data| E;
        end

        subgraph "Email Queue"
            D -->|Publishes 'approved' event| F;
            F(Kafka Topic: 'send-email-requests');
        end

        subgraph "Email Processing"
            G(Email Worker Pod);
            H(Postfix Relay Pod);
            F -->|Consumes approved event| G;
            G -->|Sends email via SMTP| H;
        end
    end

    subgraph "Internet"
        I[Resend API];
        H -->|Relays email| I;
    end
````

-----

## Monorepo Structure

The project is managed in a single repository, organized as follows:

```
/spending-transaction-monitor
├── apps/
│   ├── ingestion-service/
│   ├── rules-engine/
│   ├── email-worker/
│   └── ui/
├── packages/
│   ├── types/
│   └── ...
├── helm/
│   └── your-app-chart/
├── e2e/
│   └── tests/
└── ...
```

-----

## Core Technologies & Roles

### Development & Deployment Tools

* **Turborepo**

* **Role:** The **Monorepo Manager**. It organizes the source code and optimizes local development workflows by caching build/test results and managing tasks across all applications.

* **Helm**

* **Role:** The **Deployment Packager**. It bundles the application's container images and Kubernetes/OpenShift configurations into a single, versioned chart for easy deployment and release management.

### Application & Infrastructure Services

* **Transaction Ingestion Service:**  
  * **Purpose:** Securely receives credit card transaction data in real-time from banking systems.  
  * **Functionality:** Data validation, initial parsing, and forwarding to the Transaction Data Store.  
  * **Integration:** Connects directly with the bank's core transaction processing systems (e.g., via APIs, message queues).  
  * **Technology:** Kafka (AMQ Streams)  
* **Transaction Data Store:**  
  * **Purpose:** Stores historical and real-time transaction data for each customer.  
  * **Data:** Transaction amount, merchant details (name, category, location coordinates), timestamp, card used, transaction type (online, in-person).  
  * **Technology:** Scalable NoSQL database (e.g., MongoDB, Cassandra). Should we just use Relational DB?  
* **Online Banking Customer UI / Backend:**  
  * **Purpose:** Provides an intuitive interface for customers to define, view, modify, and delete their natural language alert rules.  
  * **Functionality:** Text input field for natural language, display of active alerts, options to enable/disable alerts.  
  * **Integration:** Communicates with the NLP Module and Alert Rules Data Store.  
  * **Technology:**  React, NodeJS, PatternFly, Express
  
  ![Spending Transaction Monitor UI](docs/images/credit-card-transacaction-monitor.png)

* **Natural Language Processing (NLP) Module:**  
  * **Purpose:** Interprets and converts natural language alert descriptions into structured, machine-readable rules.  
  * **Functionality:**  
    * **Intent Recognition:** Identifies the user's goal (e.g., "notify me if...", "alert me when...").  
    * **Entity Extraction:** Extracts key entities like amount, merchant name, location keywords (e.g., "near my home," "in New York"), timeframes (e.g., "last month," "twice as much").  
    * **Rule Generation:** Translates extracted entities and intents into a structured rule format (e.g., JSON or a custom rule language).  
  * **Technology:** Utilizes pre-trained NLP models (e.g., BERT, GPT-like models), LlamaStack, MCP Agent  
* **Alert Rules Data Store:**  
  * **Purpose:** Stores the structured, machine-readable alert rules defined by each customer.  
  * **Data:** Rule ID, customer ID, rule status (active/inactive), structured rule criteria (e.g., {"type": "amount\_threshold", "operator": "\>", "value": 500, "currency": "USD"} or {"type": "merchant\_location", "merchant\_name": "Starbucks", "location\_comparison": "near\_home"}).  
  * **Technology:** Relational database (e.g., PostgreSQL, MySQL) for structured storage and querying, or a document database.  
* **User Data Store:**  
  * **Purpose:** Stores customer-specific data relevant to alerts.  
  * **Data:** Customer address, last known mobile app location (if available and consented), last transaction location, credit limit, current balance.  
  * **Technology:** Secure relational or NoSQL database.  
* **Location Services Integration:**  
  * **Purpose:** Provides geo-coding and geo-fencing capabilities.  
  * **Functionality:** Converts addresses/locations into coordinates, calculates distances between points, determines if a point is within a defined radius.  
  * **Integration:** Leverages third-party mapping APIs (e.g., Google Maps API, OpenStreetMap API) or internal geo-spatial services.  
* **Rule Engine / Alerting Service:**  
  * **Purpose:** The core processing unit that evaluates incoming transactions against all active alert rules for the relevant customer.  
  * **Functionality:**  
    * **Transaction Matching:** Receives a new transaction and identifies the associated customer.  
    * **Rule Retrieval:** Fetches all active rules for that customer from the Alert Rules Data Store.  
    * **Evaluation:** For each rule, it retrieves necessary data (transaction details, user data, historical transactions, location data) and applies the rule logic.  
    * **Complex Logic:** Handles comparisons involving:  
      * Transaction amount, current balance, credit limit.  
      * Merchant location vs. user's address, last mobile location, last transaction location (using Location Services).  
      * Aggregations over past transactions (e.g., sum of spending in a category over a month, count of transactions).  
    * **Alert Triggering:** If a rule evaluates to true, it triggers a notification via the Notification Service.  
  * **Technology:** Event-driven architecture (e.g., Apache Kafka, RabbitMQ) for real-time processing, a rule engine framework (e.g., Drools, custom-built microservice) for evaluation logic.  
* **AI/ML Behavioral Analysis:**  
  * **Purpose:** Learns normal spending patterns for each user and identifies anomalies or trends.  
  * **Functionality:**  
    * **Baseline Creation:** Builds a profile of typical spending (e.g., average dinner spend, usual merchants, common locations).  
    * **Anomaly Detection:** Flags transactions that deviate significantly from the baseline (e.g., unusually high spend, transaction in a new category/location).  
    * **Trend Analysis:** Identifies patterns like "twice as much on dinner than before" by comparing current spend with historical averages.
    * **Rule Recommendation:** Based on detected patterns and anomalies, suggests new alert rules to the user.
  * **Integration:** Feeds insights back to the Rule Engine to enhance or supplement explicit rules, particularly for the "past transactions" user story.  
  * **Technology:** Machine learning frameworks (e.g., TensorFlow, PyTorch, Scikit-learn), potentially running on a dedicated ML platform.  
* **Notification Service:**  
  * **Purpose:** Delivers alerts to the customer through their preferred channels.  
  * **Functionality:** Supports multiple notification types (SMS, email, push notifications to mobile app).  
  * **Technology:** Integrates with third-party notification APIs (e.g., Twilio for SMS, SendGrid, Resend for email, Firebase Cloud Messaging for push) or an internal notification gateway.

### Data Flow

1. **User Defines Alert:** Customer uses the UI to input a natural language alert.  
2. **NLP Processing:** The NLP Module parses the natural language into a structured rule, which is then stored in the Alert Rules Data Store.  
3. **Transaction Ingestion:** A new credit card transaction occurs and is sent to the Transaction Ingestion Service.  
4. **Data Storage:** The transaction data is stored in the Transaction Data Store.  
5. **Rule Evaluation:** The Rule Engine / Alerting Service is triggered by the new transaction.  
   * It fetches the customer's active alert rules from the Alert Rules Data Store.  
   * It retrieves relevant user data (address, balance, limit) from the User Data Store.  
   * It queries the Transaction Data Store for historical transactions if the rule requires it.  
   * It interacts with Location Services for geo-spatial comparisons.  
   * It may consult the AI/ML Behavioral Analysis module for anomaly or trend insights.  
6. **Notification:** If any rule criteria are met, the Notification Service is invoked to send an alert to the customer.

### Addressing User Stories

* **"I want the system to recommend alerts when I navigate to the alert configuration page"**
  * **Component:** AI/ML Behavioral Analysis, Online Banking Customer UI.
  * **Mechanism:** The AI/ML Behavioral Analysis module will continuously analyze the user's transaction history and spending habits to identify patterns, common transactions, and potential areas for useful alerts (e.g., "You frequently spend over $X at this merchant, would you like an alert for transactions over $X+Y?"). These suggestions will then be presented to the user via the Online Banking Customer UI, allowing them to easily adopt or modify them into new alert rules.

* **"I want to use my own words to describe when I should be notified of a credit card transaction"**  
  * **Component:** Natural Language Processing (NLP) Module.  
  * **Mechanism:** The NLP Module is specifically designed to understand and convert free-form natural language input into structured, actionable rules.  
* **"I want to set up my alerts as individual and independent bullet items, allowing me to delete and add them as required"**  
  * **Component:** Online Banking Customer UI, Alert Rules Data Store.  
  * **Mechanism:** The UI will allow users to manage a list of distinct alert rules. Each rule, once parsed by the NLP Module, will be stored independently in the Alert Rules Data Store with a unique ID, enabling individual creation, modification, and deletion.  
* **"I want the option to use the transaction amount, current balance, and credit limit as criteria in my alert"**  
  * **Component:** NLP Module, Rule Engine / Alerting Service, User Data Store.  
  * **Mechanism:** The NLP Module will extract these criteria from the natural language. The Rule Engine will access the Transaction Data Store (for amount) and the User Data Store (for current balance and credit limit) to evaluate these conditions against the incoming transaction.  
* **"For in-person transactions, I want the ability to compare the merchant location with my address, last known (mobile app) location, and last transaction location"**  
  * **Component:** NLP Module, Location Services Integration, User Data Store, Transaction Data Store, Rule Engine / Alerting Service.  
  * **Mechanism:** The NLP Module will identify location-based comparison requests. The Rule Engine will leverage Location Services to perform geo-spatial calculations (distance, proximity) using:  
    * Merchant location (from transaction data).  
    * User's home address, last mobile location (from User Data Store).  
    * Last transaction location (from Transaction Data Store).  
* **"I should be able to account for past transactions with a given time span, for example whether I have twice as much on dinner than before, or more than a certain amount over the last month"**  
  * **Component:** NLP Module, Transaction Data Store, AI/ML Behavioral Analysis, Rule Engine / Alerting Service.  
  * **Mechanism:**  
    * The NLP Module will identify temporal and comparative language.  
    * The Rule Engine will query the Transaction Data Store for historical transactions within the specified time span (e.g., "last month").  
    * The AI/ML Behavioral Analysis module can pre-compute or assist in real-time calculations of averages, sums, or other aggregations for specific categories or merchants over time, allowing the Rule Engine to compare the current transaction against these historical patterns (e.g., "twice as much as my average dinner spend").

### Conceptual Technology Stack

* **Frontend (UI):** React, PatternFly  
* **Backend (Services):** Microservices architecture using Node.js, Python (Flask/Django), Java (Spring Boot), Go  
* **NLP:** Python with libraries like SpaCy, Hugging Face Transformers, or cloud-based NLP APIs (Google Cloud Natural Language API, AWS Comprehend)  
* **Databases:**  
  * **Transaction Data Store:** Apache Cassandra, MongoDB  
  * **Alert Rules / User Data Store:** PostgreSQL  
* **Message Queue/Event Bus:** Apache Kafka (AMQ Streams)  
* **Location Services:** Google Maps API, OpenStreetMap, Mapbox  
* **Notification:** Twilio (SMS), Resend (Email), Firebase Cloud Messaging (Push)  
* **AI/ML:** TensorFlow, PyTorch, Scikit-learn, Kubeflow (for MLOps), RHOAI, LlamaStack  
* **Deployment:** OpenShift

### Security and Privacy Considerations

* **Data Encryption:** All sensitive data (transaction details, user addresses, alert rules) must be encrypted at rest and in transit.  
* **Access Control:** Strict role-based access control (RBAC) to ensure only authorized personnel and services can access sensitive data.  
* **Authentication & Authorization:** Robust authentication for customers and secure authorization mechanisms for API calls.  
* **Compliance:** Adherence to relevant financial regulations (e.g., PCI DSS, GDPR, CCPA) and banking security standards.  
* **Privacy by Design:** Ensure that privacy considerations are built into the system from the ground up, minimizing data collection and ensuring user consent for data usage (especially location data).  
* **Audit Trails:** Comprehensive logging and auditing of all system activities, especially related to transaction processing and alert triggering.

-----

## Testing Strategy

### Unit Tests

* **What they test:** Individual functions and business logic in isolation.
* **Where they live:** Alongside the code they are testing within each application (e.g., `apps/rules-engine/src/some-rule.test.ts`).
* **Technology:** **Vitest**.

### Integration Tests

* **What they test:** The interaction between a service and its direct dependencies (e.g., the Rules Engine connecting to a real database).
* **Where they live:** Within each application's directory, in a dedicated `tests/` folder.
* **Technology:** **Vitest** + **Testcontainers**.

### End-to-End (E2E) Tests

* **What they test:** The entire system flow, from sending an HTTP request to the Ingestion Service to verifying an email was sent, as well as testing the UI.
* **Where they live:** In a top-level `e2e/` directory.
* **Technology:** **Playwright**.
