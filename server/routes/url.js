import express from 'express';
import {handleGenerateNewShortURL} from '../controllers/url.js';
const router = express.Router();

router.post('/url', handleGenerateNewShortURL);

export {router as urlRoute};