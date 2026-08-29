// Minimal HTTP surface over raw POSIX sockets: one request per connection,
// which is all a smoke check needs. Routing lives in router.cpp.
#include "router.hpp"

#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>

#include <cerrno>
#include <cstdio>
#include <cstring>
#include <iostream>
#include <sstream>
#include <string>

namespace {

void handle_connection(int client) {
  std::string raw;
  char buffer[4096];
  ssize_t n;
  while ((n = recv(client, buffer, sizeof(buffer), 0)) > 0) {
    raw.append(buffer, static_cast<size_t>(n));
    if (raw.find("\r\n\r\n") != std::string::npos) break;
  }
  std::istringstream request(raw);
  std::string method, path, version;
  request >> method >> path >> version;
  const size_t header_end = raw.find("\r\n\r\n");
  const std::string body =
      header_end == std::string::npos ? "" : raw.substr(header_end + 4);
  const size_t query = path.find('?');
  if (query != std::string::npos) path = path.substr(0, query);

  const orders::Routing routing = orders::route(method, path, body);
  std::ostringstream response;
  response << "HTTP/1.1 " << routing.status << " OK\r\n"
           << "Content-Type: application/json\r\nContent-Length: "
           << routing.body.size() << "\r\nConnection: close\r\n\r\n"
           << routing.body;
  const std::string out = response.str();
  size_t sent = 0;
  while (sent < out.size()) {
    const ssize_t w = send(client, out.data() + sent, out.size() - sent, 0);
    if (w <= 0) break;
    sent += static_cast<size_t>(w);
  }
  close(client);
}

}  // namespace

int main(int argc, char** argv) {
  const int port = argc > 1 ? std::stoi(argv[1]) : 8005;
  const int server = socket(AF_INET, SOCK_STREAM, 0);
  if (server < 0) {
    std::cerr << "orders-cpp: socket failed: " << std::strerror(errno) << "\n";
    return 1;
  }
  sockaddr_in address{};
  address.sin_family = AF_INET;
  address.sin_addr.s_addr = inet_addr("127.0.0.1");
  address.sin_port = htons(static_cast<uint16_t>(port));
  if (bind(server, reinterpret_cast<sockaddr*>(&address), sizeof(address)) < 0) {
    std::cerr << "orders-cpp: bind 127.0.0.1:" << port
              << " failed: " << std::strerror(errno) << "\n";
    return 1;
  }
  if (listen(server, 16) < 0) {
    std::cerr << "orders-cpp: listen failed: " << std::strerror(errno) << "\n";
    return 1;
  }
  std::cerr << "orders-cpp listening on " << port << "\n";
  while (true) {
    const int client = accept(server, nullptr, nullptr);
    if (client < 0) continue;
    handle_connection(client);
  }
}
