import {mongoose,Schema} from 'mongoose';

const urlSchema = new Schema({
    shortId: {
        type: String,
        required: true,
        unique: true,
    },
    redirectUrl: {
        type: String,
        required: true,
    },
    visitHistory: [{
        Timestamp: {
            type: Number
        },
    }]

}, { timestamps: true, }

);
const URL = mongoose.model('URL', urlSchema);

export {URL};