import express from "express";

import { connectDB } from "./connect.js";

import { urlRoute } from "./routes/url.js";
import { URL } from "./models/url.js"; // Importing the URL model to ensure it's registered
const app = express();
const PORT = 8001;

connectDB(
  "mongodb://kaap:kaap@mongodb/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.5.6"
)
  .then(() => {
    console.log("Connected to MongoDB");
  })
  .catch((err) => {
    console.error("Error connecting to MongoDB:", err);
  });

app.use(express.json());
app.use("/", urlRoute);
// app.get("/:shortId", async (req, res) => {
//   try {
//     const shortId = req.params.shortId;
//     const entry = await URL.findOneAndUpdate(
//       { shortId },
//       {
//         $push: {
//           visitHistory: {
//             timestamp: Date.now(),
//           },
//         },
//       },
//       { new: true } // return updated document
//     );

//     if (!entry) {
//       return res.status(404).send("Short URL not found");
//     }

//     res.redirect(entry.redirectUrl);
//   } catch (error) {
//     console.error("Error handling redirect:", error);
//     res.status(500).send("Internal Server Error");
//   }
// });

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
