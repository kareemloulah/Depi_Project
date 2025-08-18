import express from 'express';

import {connectDB} from './connect.js';

import {urlRoute} from './routes/url.js';

const app = express();
const PORT = 8001;



connectDB(process.env.MONGO_URI)
    .then(() => {
        console.log('Connected to MongoDB');
    })
    .catch((err) => {
        console.error('Error connecting to MongoDB:', err);
    });

app.use(express.json());
app.use("/url", urlRoute);

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
