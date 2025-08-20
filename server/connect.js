import mongoose from "mongoose";
mongoose.set("strictQuery", true); 
async function connectDB(url) {
  return mongoose.connect(url);
}
export { connectDB };
