import { pathToFileURL } from "node:url";
import express from "express";
import { orderTotal } from "./pricing.mjs";

const app = express();
app.use(express.json());

const orders = new Map();
let nextId = 1;

app.get("/health", (_req, res) => {
  res.json({ status: "ok" });
});

app.post("/orders", (req, res) => {
  const { customer, items } = req.body ?? {};
  if (typeof customer !== "string" || !Array.isArray(items) || items.length === 0) {
    res.status(400).json({ detail: "customer and a non-empty items list are required" });
    return;
  }
  const id = nextId++;
  const order = {
    id,
    customer,
    items,
    status: "open",
    total: orderTotal(items),
  };
  orders.set(id, order);
  res.status(201).json(order);
});

app.get("/orders", (req, res) => {
  const limit = Number(req.query.limit ?? 50);
  const offset = Number(req.query.offset ?? 0);
  res.json([...orders.values()].slice(offset, offset + limit));
});

app.get("/orders/:id", (req, res) => {
  const order = orders.get(Number(req.params.id));
  if (order === undefined) {
    res.status(404).json({ detail: `Order ${req.params.id} not found` });
    return;
  }
  res.json(order);
});

/** Start the server; tests call this and close what it returns. */
export function start(port = Number(process.env.PORT ?? 8002)) {
  return app.listen(port, "127.0.0.1");
}

const isMain =
  process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href;
if (isMain) {
  const port = Number(process.env.PORT ?? 8002);
  start(port).on("listening", () => {
    process.stdout.write(`orders-node listening on ${port}\n`);
  });
}

