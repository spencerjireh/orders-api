import { afterAll, describe, expect, it } from "vitest";
import request from "node:http";
import { start } from "../src/server.mjs";

const listener = start(0);
await new Promise((resolve) => listener.on("listening", resolve));
const port = listener.address().port;

function call(method, path, body) {
  return new Promise((resolve, reject) => {
    const data = body === undefined ? null : JSON.stringify(body);
    const req = request.request(
      { host: "127.0.0.1", port, path, method, headers: data ? { "content-type": "application/json" } : {} },
      (res) => {
        let out = "";
        res.on("data", (chunk) => (out += chunk));
        res.on("end", () => resolve({ status: res.statusCode, body: out ? JSON.parse(out) : null }));
      },
    );
    req.on("error", reject);
    if (data) req.write(data);
    req.end();
  });
}

afterAll(() => listener.close());

describe("orders routes", () => {
  it("answers health", async () => {
    const res = await call("GET", "/health");
    expect(res.status).toBe(200);
    expect(res.body).toEqual({ status: "ok" });
  });

  it("creates and reads back an order with its total", async () => {
    const created = await call("POST", "/orders", {
      customer: "ada",
      items: [{ quantity: 3, unitPrice: 19.99 }],
    });
    expect(created.status).toBe(201);
    expect(created.body.total).toBeCloseTo(59.97, 10);
    const fetched = await call("GET", `/orders/${created.body.id}`);
    expect(fetched.status).toBe(200);
    expect(fetched.body.customer).toBe("ada");
  });

  it("rejects an order with no items", async () => {
    const res = await call("POST", "/orders", { customer: "ada", items: [] });
    expect(res.status).toBe(400);
  });

  it("404s an unknown order", async () => {
    const res = await call("GET", "/orders/9999");
    expect(res.status).toBe(404);
  });
});
