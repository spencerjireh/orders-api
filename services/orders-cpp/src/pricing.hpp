// Money math for orders: every line rounds to the cent, half away from zero
// (half up for the positive prices an order carries), before the lines are
// summed. Integer cents inside; doubles only at the API edge.
#pragma once

#include <cstdint>
#include <string>
#include <vector>

namespace orders {

struct Line {
  int quantity = 0;
  double unit_price = 0.0;
};

struct Order {
  int64_t id = 0;
  std::string customer;
  std::vector<Line> items;
  std::string status = "open";
  double total = 0.0;
};

// One line's total in integer cents, rounded half up.
int64_t line_total_cents(int quantity, double unit_price);

// Sum of the rounded line totals, in dollars.
double order_total(const std::vector<Line>& items);

// Serialize an order as JSON. Hand-rolled because the exercise is the
// service, not the serializer; the fields are ours and contain no characters
// needing escape beyond what escape() handles.
std::string to_json(const Order& order);
std::string escape(const std::string& s);

}  // namespace orders
