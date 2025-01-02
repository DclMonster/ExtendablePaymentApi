import { MongoClient } from 'mongodb';
import dotenv from 'dotenv';

dotenv.config();

export class MongoService {
    private client: MongoClient;
    private db: any;
    private collection: any;

    constructor() {
        const mongoUri = process.env.MONGO_URI || 'mongodb://localhost:27017/';
        this.client = new MongoClient(mongoUri);
        this.db = this.client.db('store_db'); // Replace 'store_db' with your database name
        this.collection = this.db.collection('items'); // Replace 'items' with your collection name
    }

    async getItems(): Promise<any[]> {
        return await this.collection.find({}).toArray();
    }
} 