#include "router.hpp"

#include <mutex>
#include <sstream>
#include <stdexcept>
#include <algorithm>
#include <cctype>
#include <vector>

namespace orders {

namespace {

std::mutex g_mutex;
std::vector<Order> g_orders;
int64_t g_next_id = 1;

// Extract a JSON string value for a key anywhere in a flat-ish object.
// Returns "" when absent. The shapes this service accepts are its own
// request bodies, which carry no strings needing escape handling here.
std::string json_string_field(const std::string& body, const std::string& key) {
  const std::string needle = "\"" + key + "\"";
  size_t pos = body.find(needle);
  if (pos == std::string::npos) return "";
  pos = body.find(':', pos + needle.size());
  if (pos == std::string::npos) return "";
  pos = body.find('"', pos);
  if (pos == std::string::npos) return "";
  const size_t start = pos + 1;
  const size_t end = body.find('"', start);
  if (end == std::string::npos) return "";
  return body.substr(start, end - start);
}

// Extract a JSON number value for a key: the text from after the colon to
// the next ',' or '}'. Returns "" when absent.
std::string json_number_field(const std::string& body, const std::string& key) {
  const std::string needle = "\"" + key + "\"";
  size_t pos = body.find(needle);
  if (pos == std::string::npos) return "";
  pos = body.find(':', pos + needle.size());
  if (pos == std::string::npos) return "";
  const size_t start = pos + 1;
  const size_t comma = body.find(',', start);
  const size_t brace = body.find('}', start);
  size_t stop = std::min(comma, brace);
  if (stop == std::string::npos) stop = body.size();
  std::string text = body.substr(start, stop - start);
  while (!text.empty() && std::isspace(text.back())) text.pop_back();
  while (!text.empty() && std::isspace(text.front())) text.erase(0, 1);
  return text;
}

std::vector<Line> json_items(const std::string& body) {
  std::vector<Line> items;
  size_t pos = body.find("\"items\"");
  if (pos == std::string::npos) return items;
  pos = body.find('[', pos);
  const size_t end = body.find(']', pos);
  if (pos == std::string::npos || end == std::string::npos) return items;
  const std::string array = body.substr(pos + 1, end - pos - 1);
  size_t cursor = 0;
  while (true) {
    const size_t obj = array.find('{', cursor);
    if (obj == std::string::npos) break;
    const size_t obj_end = array.find('}', obj);
    if (obj_end == std::string::npos) break;
    const std::string item = array.substr(obj, obj_end - obj + 1);
    try {
      Line line;
      line.quantity = std::stoi(json_number_field(item, "quantity"));
      line.unit_price = std::stod(json_number_field(item, "unit_price"));
      items.push_back(line);
    } catch (const std::exception&) {
      return {};
    }
    cursor = obj_end + 1;
  }
  return items;
}

Order store_create(const std::string& customer, const std::vector<Line>& items) {
  std::lock_guard<std::mutex> lock(g_mutex);
  Order order;
  order.id = g_next_id++;
  order.customer = customer;
  order.items = items;
  order.total = order_total(items);
  g_orders.push_back(order);
  return order;
}

std::string store_list() {
  std::lock_guard<std::mutex> lock(g_mutex);
  std::ostringstream out;
  out << "[";
  for (size_t i = 0; i < g_orders.size(); ++i) {
    if (i > 0) out << ",";
    out << to_json(g_orders[i]);
  }
  out << "]";
  return out.str();
}

bool store_get(int64_t id, std::string* body) {
  std::lock_guard<std::mutex> lock(g_mutex);
  for (const Order& order : g_orders) {
    if (order.id == id) {
      *body = to_json(order);
      return true;
    }
  }
  return false;
}

}  // namespace

void reset_store() {
  std::lock_guard<std::mutex> lock(g_mutex);
  g_orders.clear();
  g_next_id = 1;
}

Routing route(const std::string& method, const std::string& path,
              const std::string& body) {
  if (method == "GET" && path == "/health") {
    return {200, "{\"status\":\"ok\"}"};
  }
  if (method == "POST" && path == "/orders") {
    const std::string customer = json_string_field(body, "customer");
    const std::vector<Line> items = json_items(body);
    if (customer.empty() || items.empty()) {
      return {400, "{\"detail\":\"customer and a non-empty items list are required\"}"};
    }
    return {201, to_json(store_create(customer, items))};
  }
  if (method == "GET" && path == "/orders") {
    return {200, store_list()};
  }
  if (method == "GET" && path.rfind("/orders/", 0) == 0) {
    try {
      const int64_t id = std::stoll(path.substr(8));
      std::string found;
      if (store_get(id, &found)) {
        return {200, found};
      }
      return {404, "{\"detail\":\"order not found\"}"};
    } catch (const std::exception&) {
      return {400, "{\"detail\":\"order id must be an integer\"}"};
    }
  }
  return {404, "{\"detail\":\"not found\"}"};
}

}  // namespace orders
