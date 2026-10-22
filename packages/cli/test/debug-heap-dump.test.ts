import { expect, test } from "bun:test"
import fs from "node:fs/promises"
import path from "node:path"
import { ServiceConfig } from "../src/services/service-config"
import { OPENCODE_VERSION } from "../src/version"
import { isolatedEnv } from "./fixture/environment"
import { tmpdir } from "./fixture/tmpdir"

// The server owns the snapshot writer (packages/server/test/heap-dump.test.ts); these cover how the
// command finds a server, what it prints, and that it never starts or replaces one.

test("prints the snapshot path from the registered server without replacing it", async () => {
  await using root = await tmpdir()
  const requests: Array<{ method: string; path: string; authorization: string | null }> = []
  using server = fake((request) => {
    requests.push({
      method: request.method,
      path: new URL(request.url).pathname,
      authorization: request.headers.get("authorization"),
    })
    return Response.json({ path: "/server/log/heap-1-2.heapsnapshot", pid: process.pid })
  })
  const registration = await register(root.path, server.url.href)

  const result = await cli(root.path, ["debug", "heap-dump"])

  expect({ code: result.code, stderr: result.stderr, stdout: result.stdout.trim() }).toEqual({
    code: 0,
    stderr: "",
    stdout: "/server/log/heap-1-2.heapsnapshot",
  })
  expect(requests).toEqual([
    { method: "POST", path: "/api/debug/heap-dump", authorization: `Basic ${btoa("opencode:secret")}` },
  ])
  expect(await Bun.file(registration.file).json()).toEqual(registration.info)
})

test("fails without starting a server when none is registered", async () => {
  await using root = await tmpdir()

  const result = await cli(root.path, ["debug", "heap-dump"])

  expect(result.stderr).toContain("No background server is running")
  expect(result.code).toBe(1)
  expect(await Bun.file(path.join(root.path, "state", "opencode", ServiceConfig.filename())).exists()).toBe(false)
})

test("explains when the server predates heap dumps", async () => {
  await using root = await tmpdir()
  using server = fake(() => new Response(null, { status: 404 }))

  const result = await cli(root.path, ["debug", "heap-dump", "--server", server.url.href], {
    OPENCODE_PASSWORD: "secret",
  })

  expect(result.stderr.trim()).toBe(
    `The server at ${server.url.href} does not support heap dumps. Update and restart it first.`,
  )
  expect(result.code).toBe(1)
})

// Answers the health probe like a ready V2 server and passes every other request to `handle`.
function fake(handle: (request: Request) => Response) {
  return Bun.serve({
    hostname: "127.0.0.1",
    port: 0,
    fetch: (request) =>
      new URL(request.url).pathname === "/api/info"
        ? Response.json({ version: OPENCODE_VERSION, pid: process.pid, urls: [] })
        : handle(request),
  })
}

async function register(root: string, url: string) {
  const file = path.join(root, "state", "opencode", ServiceConfig.filename())
  const info = { version: OPENCODE_VERSION, url, pid: process.pid, password: "secret" }
  await fs.mkdir(path.dirname(file), { recursive: true })
  await fs.writeFile(file, JSON.stringify(info))
  return { file, info }
}

async function cli(root: string, args: string[], env: Record<string, string> = {}) {
  const child = Bun.spawn([process.execPath, "run", path.join(import.meta.dir, "../src/index.ts"), ...args], {
    cwd: path.join(import.meta.dir, ".."),
    env: isolatedEnv(root, env),
    stdout: "pipe",
    stderr: "pipe",
  })
  const [stdout, stderr, code] = await Promise.all([
    new Response(child.stdout).text(),
    new Response(child.stderr).text(),
    child.exited,
  ])
  return { stdout, stderr, code }
}
