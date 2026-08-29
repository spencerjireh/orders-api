package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestHealth(t *testing.T) {
	rec := httptest.NewRecorder()
	health(rec, httptest.NewRequest(http.MethodGet, "/health", nil))
	if rec.Code != http.StatusOK {
		t.Fatalf("health status = %d", rec.Code)
	}
	if !strings.Contains(rec.Body.String(), "ok") {
		t.Fatalf("health body = %s", rec.Body.String())
	}
}

func TestCreateAndGetOrder(t *testing.T) {
	clearStore()

	body, _ := json.Marshal(createRequest{Customer: "ada", Items: []Line{{Quantity: 3, UnitPrice: 19.99}}})
	rec := httptest.NewRecorder()
	createOrder(rec, httptest.NewRequest(http.MethodPost, "/orders", bytes.NewReader(body)))
	if rec.Code != http.StatusCreated {
		t.Fatalf("create status = %d: %s", rec.Code, rec.Body.String())
	}
	var created order
	if err := json.Unmarshal(rec.Body.Bytes(), &created); err != nil {
		t.Fatalf("create body: %v", err)
	}
	if fmt.Sprintf("%.2f", created.Total) != "59.97" {
		t.Fatalf("total = %v, want 59.97", created.Total)
	}

	req := httptest.NewRequest(http.MethodGet, fmt.Sprintf("/orders/%d", created.ID), nil)
	req.SetPathValue("id", fmt.Sprintf("%d", created.ID))
	rec = httptest.NewRecorder()
	getOrder(rec, req)
	if rec.Code != http.StatusOK {
		t.Fatalf("get status = %d: %s", rec.Code, rec.Body.String())
	}
}

func TestGetUnknownOrderIs404(t *testing.T) {
	clearStore()
	req := httptest.NewRequest(http.MethodGet, "/orders/9999", nil)
	req.SetPathValue("id", "9999")
	rec := httptest.NewRecorder()
	getOrder(rec, req)
	if rec.Code != http.StatusNotFound {
		t.Fatalf("status = %d, want 404", rec.Code)
	}
}

func TestCreateRejectsEmptyItems(t *testing.T) {
	clearStore()
	body, _ := json.Marshal(createRequest{Customer: "ada"})
	rec := httptest.NewRecorder()
	createOrder(rec, httptest.NewRequest(http.MethodPost, "/orders", bytes.NewReader(body)))
	if rec.Code != http.StatusBadRequest {
		t.Fatalf("status = %d, want 400", rec.Code)
	}
}

func clearStore() {
	mu.Lock()
	defer mu.Unlock()
	orders = map[int64]order{}
	nextID = 1
}
