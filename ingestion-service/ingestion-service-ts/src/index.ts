import express, { Request, Response } from 'express';
import { Kafka } from 'kafkajs';
import { Transaction, IncomingTransaction } from '../common/models';

const app = express();
app.use(express.json());

const kafkaHost = process.env.KAFKA_HOST || 'localhost';
const kafkaPort = process.env.KAFKA_PORT || '9092';

const kafka = new Kafka({
    clientId: 'ingestion-service-ts',
    brokers: [`${kafkaHost}:${kafkaPort}`]
});

const producer = kafka.producer();

const transactionRouter = express.Router();

function transformTransaction(incoming: IncomingTransaction): Transaction {
    return {
        user: incoming.User,
        card: incoming.Card,
        year: incoming.Year,
        month: incoming.Month,
        day: incoming.Day,
        time: incoming.Time,
        amount: parseFloat(incoming.Amount.replace('$', '')),
        use_chip: incoming["Use Chip"],
        merchant_id: incoming["Merchant Name"],
        merchant_city: incoming["Merchant City"],
        merchant_state: incoming["Merchant State"],
        zip: incoming["Zip"],
        mcc: incoming.MCC,
        errors: incoming["Errors?"],
        is_fraud: incoming["Is Fraud?"] === 'Yes',
    };
}

transactionRouter.post('/', async (req: Request, res: Response) => {
    const incomingTransaction: IncomingTransaction = req.body;
    const transaction = transformTransaction(incomingTransaction);
    try {
        await producer.send({
            topic: 'transactions',
            messages: [{ value: JSON.stringify(transaction) }],
        });
        console.log('Message sent to Kafka:', transaction);
        res.status(200).json(transaction);
    } catch (error) {
        console.error('Error sending message to Kafka:', error);
        res.status(500).send('Error sending message to Kafka');
    }
});

const healthzRouter = express.Router();
healthzRouter.get('/', (req: Request, res: Response) => {
    res.status(200).json({status: 'ok'});
});

const run = async () => {
    await producer.connect();
    if (require.main === module) {
        const port = process.env.PORT || 3000;
        app.use('/transactions', transactionRouter);
        app.use('/healthz', healthzRouter);
        app.listen(port, () => {
            console.log(`Server is running on port ${port}`);
        });
    }
};

run().catch(console.error);

process.on('SIGINT', async () => {
    await producer.disconnect();
    process.exit();
});

module.exports = {transactionRouter, healthzRouter};
