#include "pricing.hpp"

#include <cmath>
#include <cstdio>
#include <sstream>

namespace orders {

int64_t line_total_cents(int quantity, double unit_price) {
  return static_cast<int64_t>(std::llround(quantity * unit_price * 100.0));
}

double order_total(const std::vector<Line>& items) {
  int64_t cents = 0;
  for (const Line& item : items) {
    cents += line_total_cents(item.quantity, item.unit_price);
  }
  return static_cast<double>(cents) / 100.0;
}

std::string escape(const std::string& s) {
  std::string out;
  for (char c : s) {
    switch (c) {
      case '"': out += "\\\""; break;
      case '\\': out += "\\\\"; break;
      case '\n': out += "\\n"; break;
      case '\t': out += "\\t"; break;
      default: out += c; break;
    }
  }
  return out;
}

std::string to_json(const Order& order) {
  std::ostringstream items;
  for (size_t i = 0; i < order.items.size(); ++i) {
    if (i > 0) items << ",";
    items << "{\"quantity\":" << order.items[i].quantity
          << ",\"unit_price\":" << order.items[i].unit_price << "}";
  }
  std::ostringstream out;
  out << "{\"id\":" << order.id << ",\"customer\":\"" << escape(order.customer)
      << "\",\"items\":[" << items.str() << "],\"status\":\"" << order.status
      << "\",\"total\":";
  char total[32];
  std::snprintf(total, sizeof(total), "%.2f", order.total);
  out << total << "}";
  return out.str();
}

}  // namespace orders
