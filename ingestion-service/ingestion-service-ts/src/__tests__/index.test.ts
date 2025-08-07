import request from 'supertest';
import express from 'express';
import { Kafka } from 'kafkajs';

const mockSend = jest.fn(() => Promise.resolve());
jest.mock('kafkajs', () => {
    const originalKafka = jest.requireActual('kafkajs');
    return {
        ...originalKafka,
        Kafka: jest.fn().mockImplementation(() => ({
            producer: jest.fn(() => ({
                connect: jest.fn(() => Promise.resolve()),
                send: mockSend,
                disconnect: jest.fn(() => Promise.resolve()),
            })),
        })),
    };
});

const app = express();
app.use(express.json());
const { transactionRouter, healthzRouter } = require('../index');
app.use('/transactions', transactionRouter);
app.use('/healthz', healthzRouter);

app.get('/healthz', (req, res) => {
    res.status(200).json({status: 'ok'});
});

describe('GET /healthz', () => {
    it('should return 200 OK', async () => {
        const response = await request(app)
            .get('/healthz')
            .send();
        expect(response.status).toBe(200);
        expect(response.body).toEqual({status: 'ok'});
    });
});

describe('POST /transactions', () => {
  it('should send a message to Kafka and return the transaction', async () => {
    const incomingTransaction = {
        "User": 1,
        "Card": 1,
        "Year": 2023,
        "Month": 1,
        "Day": 1,
        "Time": "12:00:00",
        "Amount": "$10.00",
        "Use Chip": "Swipe Transaction",
        "Merchant Name": 123456789,
        "Merchant City": "New York",
        "Merchant State": "NY",
        "Zip": "10001",
        "MCC": 5411,
        "Errors?": "",
        "Is Fraud?": "No"
    };

    const response = await request(app)
      .post('/transactions')
      .send(incomingTransaction);

    expect(response.status).toBe(200);

    const expectedTransaction = {
        "user": 1,
        "card": 1,
        "year": 2023,
        "month": 1,
        "day": 1,
        "time": "12:00:00",
        "amount": 10.00,
        "use_chip": "Swipe Transaction",
        "merchant_id": 123456789,
        "merchant_city": "New York",
        "merchant_state": "NY",
        "zip": "10001",
        "mcc": 5411,
        "errors": "",
        "is_fraud": false
    };

    expect(response.body).toEqual(expectedTransaction);
    expect(mockSend).toHaveBeenCalledWith({
        topic: 'transactions',
        messages: [{ value: JSON.stringify(expectedTransaction) }],
    });
  });
});
