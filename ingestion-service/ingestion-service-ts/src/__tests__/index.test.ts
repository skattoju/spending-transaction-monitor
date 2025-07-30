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
    const transaction = {
        user_id: 1,
        card_id: 1,
        amount: 10.0,
        description: 'test',
    };

    const response = await request(app)
      .post('/transactions')
      .send(transaction);

    expect(response.status).toBe(200);
    expect(response.body).toEqual(transaction);
    expect(mockSend).toHaveBeenCalledWith({
        topic: 'transactions',
        messages: [{ value: JSON.stringify(transaction) }],
    });
  });
});
