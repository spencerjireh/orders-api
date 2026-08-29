// Exercises the real router (src/router.cpp), the same code the server calls
// per request.
#include "router.hpp"

#include <cstdio>
#include <string>

namespace {

int failures = 0;

void check(bool ok, const std::string& what) {
  if (!ok) {
    std::fprintf(stderr, "FAILED: %s\n", what.c_str());
    ++failures;
  }
}

}  // namespace

int main() {
  orders::reset_store();

  orders::Routing r = orders::route("GET", "/health", "");
  check(r.status == 200 && r.body.find("ok") != std::string::npos, "health");

  r = orders::route("POST", "/orders",
                    "{\"customer\":\"ada\",\"items\":[{\"quantity\":3,\"unit_price\":19.99}]}");
  check(r.status == 201, "create status 201");
  check(r.body.find("\"total\":59.97") != std::string::npos,
        "create total 59.97: " + r.body);
  const std::string created = r.body;

  r = orders::route("POST", "/orders", "{\"customer\":\"ada\",\"items\":[]}");
  check(r.status == 400, "empty items 400");

  r = orders::route("GET", "/orders", "");
  check(r.status == 200 && r.body.find(created) != std::string::npos, "list");

  r = orders::route("GET", "/orders/1", "");
  check(r.status == 200 && r.body == created, "get by id");

  r = orders::route("GET", "/orders/9999", "");
  check(r.status == 404, "unknown order 404");

  r = orders::route("GET", "/orders/abc", "");
  check(r.status == 400, "non-integer id 400");

  r = orders::route("GET", "/nope", "");
  check(r.status == 404, "unknown path 404");

  if (failures == 0) {
    std::printf("all router tests passed\n");
    return 0;
  }
  return 1;
}
