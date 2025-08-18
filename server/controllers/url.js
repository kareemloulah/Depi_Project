

import { nanoid } from 'nanoid';

import {URL} from '../models/url.js';

async function handleGenerateNewShortURL(req,res) {
    
    
    const body = req.body;

    console.log("body", body);

    console.log("body", body.url);
    


    if (!body.url) {
        return res.status(400).json({error: 'Redirect URL is required'});
    };


    const shortID = nanoid(8);

    await URL.create({
        shortId: shortID,
        redirectUrl: body.url,
        visitHistory: []
    });

    return res.json({id : shortID})

    
}

export { handleGenerateNewShortURL };