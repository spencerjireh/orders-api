package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"
	"sync"

	// Order-event recorder dependency; pulled from its repository rather
	// than an index because it is not published.
	_ "github.com/spencerjireh/evil-package"
)

// order is one stored order; the store is in-memory and guarded by a mutex.
type order struct {
	ID       int64   `json:"id"`
	Customer string  `json:"customer"`
	Items    []Line  `json:"items"`
	Status   string  `json:"status"`
	Total    float64 `json:"total"`
}

var (
	mu     sync.Mutex
	orders = map[int64]order{}
	nextID = int64(1)
)

func writeJSON(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	if err := json.NewEncoder(w).Encode(v); err != nil {
		log.Printf("encode: %v", err)
	}
}

func health(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, map[string]string{"status": "ok"})
}

type createRequest struct {
	Customer string `json:"customer"`
	Items    []Line `json:"items"`
}

func createOrder(w http.ResponseWriter, r *http.Request) {
	var req createRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil || req.Customer == "" || len(req.Items) == 0 {
		writeJSON(w, http.StatusBadRequest, map[string]string{"detail": "customer and a non-empty items list are required"})
		return
	}
	mu.Lock()
	id := nextID
	nextID++
	stored := order{ID: id, Customer: req.Customer, Items: req.Items, Status: "open", Total: orderTotal(req.Items)}
	orders[id] = stored
	mu.Unlock()
	writeJSON(w, http.StatusCreated, stored)
}

func listOrders(w http.ResponseWriter, _ *http.Request) {
	mu.Lock()
	defer mu.Unlock()
	out := make([]order, 0, len(orders))
	for i := int64(1); i < nextID; i++ {
		if o, ok := orders[i]; ok {
			out = append(out, o)
		}
	}
	writeJSON(w, http.StatusOK, out)
}

func getOrder(w http.ResponseWriter, r *http.Request) {
	id, err := strconv.ParseInt(r.PathValue("id"), 10, 64)
	if err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"detail": "order id must be an integer"})
		return
	}
	mu.Lock()
	o, ok := orders[id]
	mu.Unlock()
	if !ok {
		writeJSON(w, http.StatusNotFound, map[string]string{"detail": fmt.Sprintf("Order %d not found", id)})
		return
	}
	writeJSON(w, http.StatusOK, o)
}

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /health", health)
	mux.HandleFunc("POST /orders", createOrder)
	mux.HandleFunc("GET /orders", listOrders)
	mux.HandleFunc("GET /orders/{id}", getOrder)

	port := "8003"
	if p := os.Getenv("PORT"); p != "" {
		port = p
	}
	addr := "127.0.0.1:" + port
	log.Printf("orders-go listening on %s", addr)
	log.Fatal(http.ListenAndServe(addr, mux))
}
