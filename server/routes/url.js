import express from 'express';
import {handleGenerateNewShortURL} from '../controllers/url.js';
const router = express.Router();

router.post('/', handleGenerateNewShortURL);

export {router as urlRoute};