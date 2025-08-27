import express from "express";
import cors from "cors";
import { connectDB } from "./connect.js";
import { urlRoute } from "./routes/url.js";
import { URL } from "./models/url.js";

/*
  Create Express app instance and read port from environment.
  PORT should be defined in your environment (e.g. via .env or your deployment).
*/
const app = express();
const PORT = process.env.PORT;

// Configure CORS:
// - By default allows all origins: app.use(cors())
// - To restrict, set ALLOWED_ORIGINS as a comma-separated env var

app.use(
  cors(
    {
      origin: "*",   // or "*" for testing
      methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
      allowedHeaders: ["Content-Type", "Authorization"]
    }
  )
);

/*
  Connect to MongoDB using the helper connectDB function.
  connectDB returns a Promise so we log success or errors here.
  MONGO_URI should be set in your environment.
*/
connectDB(`${process.env.MONGO_URI}`)
  .then(() => {
    console.log("Connected to MongoDB");
  })
  .catch((err) => {
    console.error("Error connecting to MongoDB:", err);
  });

// Enable parsing of JSON request bodies for all routes.
app.use(express.json());

// Mount route handlers defined in ./routes/url.js at the root path.
app.use("/", urlRoute);

/*
  Redirect /:shortId
  - Finds the URL document by shortId
  - Adds a new visit entry (timestamp) to visitHistory using findOneAndUpdate
  - Returns the redirectUrl and shortId as JSON (caller can perform the redirect)
  - If entry not found -> 404
  - On error -> 500
*/
app.get("/:shortId", async (req, res) => {
  try {
    const shortId = req.params.shortId;

    // Atomically push a visit record and return the updated document
    const entry = await URL.findOneAndUpdate(
      { shortId },
      {
        $push: {
          visitHistory: {
            timestamp: Date.now(),
          },
        },
      },
      { new: true } // return the updated document
    );

    if (!entry) {
      // No document found with the provided shortId
      return res.status(404).send("Short URL not found");
    }

    // Respond with URL info (client can redirect to entry.redirectUrl)
    res.json({
      redirectUrl: entry.redirectUrl,
      shortId: entry.shortId,
    });
  } catch (error) {
    console.error("Error handling redirect:", error);
    res.status(500).send("Internal Server Error");
  }
});

/*
  Analytics endpoint: GET /analytics/:shortId
  - Retrieves the URL document by shortId
  - Returns visitHistory and visitCount
  - If entry not found -> 404
  - On error -> 500
*/
app.get("/analytics/:shortId", async (req, res) => {
  try {
    const shortId = req.params.shortId;

    // Find the URL document (no update required)
    const entry = await URL.findOne({ shortId });

    if (!entry) {
      return res.status(404).send("Short URL not found");
    }

    // Return analytics data
    res.json({
      shortId: entry.shortId,
      visitHistory: entry.visitHistory,
      visitCount: entry.visitHistory.length,
    });
  } catch (error) {
    console.error("Error handling redirect:", error);
    res.status(500).send("Internal Server Error");
  }
});

// Start the HTTP server and listen on the configured port.
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
