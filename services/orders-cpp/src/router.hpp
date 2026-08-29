// Routing and request parsing, shared by the server and its tests.
#pragma once

#include <string>

#include "pricing.hpp"

namespace orders {

struct Routing {
  int status = 500;
  std::string body;
};

// Route one request. `body` is the request body after the headers.
Routing route(const std::string& method, const std::string& path,
              const std::string& body);

// Reset the in-memory store (tests only).
void reset_store();

}  // namespace orders
