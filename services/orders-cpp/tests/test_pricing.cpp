#include "pricing.hpp"

#include <cmath>
#include <cstdio>
#include <string>

#include <cassert>

using orders::Line;
using orders::line_total_cents;
using orders::order_total;

static void check(bool ok, const std::string& what) {
  if (!ok) {
    std::fprintf(stderr, "FAILED: %s\n", what.c_str());
    std::exit(1);
  }
}

int main() {
  check(line_total_cents(3, 19.99) == 5997, "3 x 19.99 = 5997c");
  check(line_total_cents(1, 0.125) == 13, "1 x 0.125 rounds half up to 13c");
  check(line_total_cents(2, 0.125) == 25, "2 x 0.125 = 25c");
  check(line_total_cents(2, 10.05) == 2010, "2 x 10.05 = 2010c");
  check(line_total_cents(1, 0.1) == 10, "1 x 0.1 = 10c");

  const double total = order_total({Line{3, 19.99}, Line{2, 5.0}});
  check(std::abs(total - 69.97) < 1e-9, "rounded lines sum to 69.97");
  check(order_total({}) == 0.0, "empty order totals zero");

  const orders::Order order{7, "ada \"a\"", {{3, 19.99}}, "open", 59.97};
  const std::string json = orders::to_json(order);
  check(json.find("\"customer\":\"ada \\\"a\\\"\"") != std::string::npos,
        "customer quotes escaped: " + json);
  check(json.find("\"total\":59.97") != std::string::npos, "total serialized");

  std::printf("all pricing tests passed\n");
  return 0;
}
