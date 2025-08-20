import mongoose from "mongoose";
mongoose.set("strictQuery", true); // Disable strict query mode
async function connectDB(url) {
  return mongoose.connect(url);
}
export { connectDB };
