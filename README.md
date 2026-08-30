# orders-api

A polyglot demo monorepo: the same small orders service, written six ways.
Cujo, an execution-backed pull request reviewer, uses this repo as its
protected target, so every PR here is an exercise for its inference and its
sensors, not just for the code.

The Cujo policy (`.cujo.yml`) is deliberately empty. How to install, test,
and boot each service is discoverable the way a developer discovers it: the
service's manifest and its CI workflow under `.github/workflows/`.

## Services

| Service       | Language | Manifest         | Test command            | Boot command                                   | Port |
| ------------- | -------- | ---------------- | ----------------------- | ---------------------------------------------- | ---- |
| `orders-py`   | Python   | `pyproject.toml` | `python -m pytest -q`   | `uvicorn app.main:app --port 8001`             | 8001 |
| `orders-node` | Node     | `package.json`   | `npm test`              | `node src/server.mjs`                          | 8002 |
| `orders-go`   | Go       | `go.mod`         | `go test ./...`         | `go run .`                                     | 8003 |
| `orders-rust` | Rust     | `Cargo.toml`     | `cargo test`            | `cargo run`                                    | 8004 |
| `orders-cpp`  | C++      | `conanfile.txt`  | `ctest` (CMake build)   | `./build/orders-cpp 8005`                      | 8005 |
| `orders-php`  | PHP      | `composer.json`  | `vendor/bin/phpunit`    | `php -S 127.0.0.1:8006 public/index.php`       | 8006 |

Every service implements the same surface — `GET /health`, `POST /orders`,
`GET /orders`, `GET /orders/{id}` — with an in-memory store, and the same
money rule: each line rounds to the cent, half up, before the lines are
summed. The rule is pinned by a test in every service, in every language.

Commands run inside the service directory. `orders-cpp` configures with
`cmake -S . -B build && cmake --build build` and tests with
`ctest --test-dir build --output-on-failure`.

## Why six

One repo, six ecosystems, six dependency manifests, six test runners. A pull
request here can change one service or several, add a dependency in any of
`requirements.txt`, `package.json`, `go.mod`, `Cargo.toml`, `conanfile.txt`,
or `composer.json`, and the reviewer has to work out which install, which
suite, and which boot the change touches — from the repository alone.

## Reading a review

Every pull request here gets one review from `cujo-guard[bot]`. The verdict on
the first line is the whole summary: a blocking review names something a sensor
observed on this head, and an advisory one does not. The Coverage section says
which checks ran and which did not, so a quiet review and an unrun check are
never the same thing.
