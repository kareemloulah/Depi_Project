
import mongoose from 'mongoose';
async function connectDB(url) {
    return mongoose.connect(url)
}

export { connectDB };