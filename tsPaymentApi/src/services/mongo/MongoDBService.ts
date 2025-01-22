import { MongoClient, Db } from 'mongodb';

export abstract class MongoDBService {
    private readonly client: MongoClient;
    protected readonly db: Db;

    constructor(databaseName: string = 'Store') {
        const mongoUri = process.env.MONGO_URI || 'mongodb://localhost:27017/';
        this.client = new MongoClient(mongoUri);
        this.db = this.client.db(databaseName);
    }

    protected async connect(): Promise<void> {
        try {
            await this.client.connect();
        } catch (error) {
            console.error('Failed to connect to MongoDB:', error);
            throw error;
        }
    }

    protected async disconnect(): Promise<void> {
        try {
            await this.client.close();
        } catch (error) {
            console.error('Failed to disconnect from MongoDB:', error);
            throw error;
        }
    }
} 