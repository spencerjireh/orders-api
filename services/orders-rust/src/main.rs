//! Demo Rust orders service: /health, POST /orders, GET /orders, GET /orders/{id}.

mod pricing;

use std::sync::atomic::{AtomicI64, Ordering};
use std::sync::Mutex;

use serde::{Deserialize, Serialize};
use tiny_http::{Header, Method, Response, Server};

use crate::pricing::Line;

static NEXT_ID: AtomicI64 = AtomicI64::new(1);

#[derive(Debug, Clone, Serialize)]
pub struct Order {
    pub id: i64,
    pub customer: String,
    pub items: Vec<Line>,
    pub status: &'static str,
    pub total: f64,
}

#[derive(Debug, Deserialize)]
pub struct CreateRequest {
    pub customer: String,
    pub items: Vec<Line>,
}

#[derive(Default)]
pub struct Store {
    orders: Mutex<Vec<Order>>,
}

impl Store {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn create(&self, req: CreateRequest) -> Order {
        let order = Order {
            id: NEXT_ID.fetch_add(1, Ordering::SeqCst),
            customer: req.customer,
            total: crate::pricing::order_total(&req.items),
            items: req.items,
            status: "open",
        };
        self.orders.lock().unwrap().push(order.clone());
        order
    }

    pub fn list(&self) -> Vec<Order> {
        self.orders.lock().unwrap().clone()
    }

    pub fn get(&self, id: i64) -> Option<Order> {
        self.orders.lock().unwrap().iter().find(|o| o.id == id).cloned()
    }
}

fn json_header() -> Header {
    Header::from_bytes(&b"Content-Type"[..], &b"application/json"[..]).unwrap()
}

fn detail(status: u16, message: &str) -> (u16, String) {
    (
        status,
        serde_json::json!({ "detail": message }).to_string(),
    )
}

fn main() {
    let port: u16 = std::env::var("PORT")
        .ok()
        .and_then(|p| p.parse().ok())
        .unwrap_or(8004);
    serve(port);
}

fn serve(port: u16) -> ! {
    let store = Store::new();
    let server = Server::http(("127.0.0.1", port)).unwrap_or_else(|e| {
        eprintln!("orders-rust: bind 127.0.0.1:{port} failed: {e}");
        std::process::exit(1);
    });
    eprintln!("orders-rust listening on {port}");
    for mut request in server.incoming_requests() {
        let url = request.url().to_string();
        let method = request.method().clone();
        let mut body = String::new();
        let _ = request.as_reader().read_to_string(&mut body);
        let (status, payload) = route(&store, &method, &url, &body);
        let response = Response::from_string(payload)
            .with_status_code(status)
            .with_header(json_header());
        let _ = request.respond(response);
    }
    unreachable!("Server::incoming_requests never ends");
}

fn route(store: &Store, method: &Method, url: &str, body: &str) -> (u16, String) {
    match (method, url) {
        (Method::Get, "/health") => (
            200,
            serde_json::json!({ "status": "ok" }).to_string(),
        ),
        (Method::Post, "/orders") => match serde_json::from_str::<CreateRequest>(body) {
            Ok(req) if !req.customer.is_empty() && !req.items.is_empty() => {
                let order = store.create(req);
                (201, serde_json::to_string(&order).unwrap())
            }
            Ok(_) => detail(400, "customer and a non-empty items list are required"),
            Err(_) => detail(400, "body must be a create-order payload"),
        },
        (Method::Get, "/orders") => (
            200,
            serde_json::to_string(&store.list()).unwrap(),
        ),
        _ if url.starts_with("/orders/") => match url["/orders/".len()..].parse::<i64>() {
            Ok(id) if *method == Method::Get => match store.get(id) {
                Some(order) => (200, serde_json::to_string(&order).unwrap()),
                None => detail(404, &format!("Order {id} not found")),
            },
            Ok(_) => detail(405, "method not allowed"),
            Err(_) => detail(400, "order id must be an integer"),
        },
        _ => detail(404, "not found"),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::pricing::Line;

    fn req(payload: &str) -> CreateRequest {
        serde_json::from_str(payload).unwrap()
    }

    #[test]
    fn create_then_get_round_trip() {
        let store = Store::new();
        let order = store.create(req(
            r#"{"customer":"ada","items":[{"quantity":3,"unit_price":19.99}]}"#,
        ));
        assert!((order.total - 59.97).abs() < 1e-9);
        assert_eq!(store.get(order.id).unwrap().customer, "ada");
    }

    #[test]
    fn create_rejects_empty_items_at_the_route() {
        let store = Store::new();
        let (status, _) = route(
            &store,
            &Method::Post,
            "/orders",
            r#"{"customer":"ada","items":[]}"#,
        );
        assert_eq!(status, 400);
    }

    #[test]
    fn unknown_order_is_404() {
        let store = Store::new();
        let (status, _) = route(&store, &Method::Get, "/orders/9999", "");
        assert_eq!(status, 404);
    }

    #[test]
    fn health_is_ok() {
        let store = Store::new();
        let (status, body) = route(&store, &Method::Get, "/health", "");
        assert_eq!(status, 200);
        assert!(body.contains("ok"));
    }
}
