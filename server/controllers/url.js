/**
 * Controller for URL-related operations.
 * - Validates incoming requests
 * - Generates a short ID for the provided redirect URL
 * - Persists a URL document to MongoDB
 * - Returns the generated short ID to the caller
 */

import { nanoid } from "nanoid";
import { URL } from "../models/url.js";

/**
 * POST / (or whichever route mounts this controller)
 * Expected body: { url: "<destination-url>" }
 *
 * Steps:
 * 1. Read request body
 * 2. Validate that a redirect URL is provided
 * 3. Generate a short identifier using nanoid(8)
 * 4. Create a new URL document in the database with an empty visitHistory
 * 5. Respond with the generated short id
 *
 * Returns:
 * - 400 + JSON error when body.url is missing
 * - 200 + JSON { id: shortId } on success
 */
async function handleGenerateNewShortURL(req, res) {
  // Request payload (should include `url`)
  const body = req.body;

  // Simple logging for debugging (can be removed or replaced with a logger)
  console.log("body", body);
  console.log("body.url", body?.url);

  // Validate input: the redirect URL is required
  if (!body || !body.url) {
    // 400 Bad Request when required data is missing
    return res.status(400).json({ error: "Redirect URL is required" });
  }

  // Generate a short ID (8 characters) to use as the short URL key
  const shortID = nanoid(8);

  // Persist the new short URL document to the database.
  // visitHistory starts empty and will be populated when the short URL is visited.
  await URL.create({
    shortId: shortID,
    redirectUrl: body.url,
    visitHistory: [],
  });

  // Return the generated short id to the client.
  return res.json({ id: shortID });
}

export { handleGenerateNewShortURL };
