import { expect } from "bun:test"
import fs from "node:fs/promises"
import path from "node:path"
import { Global } from "@opencode/util/global"
import { Effect } from "effect"
import { tmpdir } from "../../core/test/fixture/tmpdir"
import { it } from "../../core/test/lib/effect"
import { ServerFetch } from "../src/fetch"

const authorization = `Basic ${btoa("opencode:secret")}`

const server = Effect.fnUntraced(function* (root: string) {
  const log = path.join(root, "log")
  const handler = yield* ServerFetch.make(
    {
      app: { version: "test-version" },
      password: "secret",
      database: { path: ":memory:" },
      config: { project: false, directory: path.join(root, "config") },
      models: { fetch: false },
      fs: { filewatcher: false },
    },
    { overrides: [Global.node.replace(Global.layerWith({ config: path.join(root, "config"), log }))] },
  )
  const dump = (headers: Record<string, string> = { authorization }) =>
    Effect.promise(() => handler(new Request("http://opencode.local/api/debug/heap-dump", { method: "POST", headers })))
  return { log, dump }
})

// Each snapshot serializes the whole test process heap, which takes seconds on Windows CI.
it.live(
  "writes completed private snapshots of the server process, one at a time",
  () =>
    Effect.gen(function* () {
      const root = yield* Effect.acquireDisposable(Effect.promise(() => tmpdir("opencode-heap-dump-")))
      const api = yield* server(root.path)

      expect((yield* api.dump({})).status).toBe(401)

      const responses = yield* Effect.all([api.dump(), api.dump()], { concurrency: "unbounded" })
      expect(responses.map((response) => response.status)).toEqual([200, 200])
      const results = yield* Effect.promise(() =>
        Promise.all(responses.map((response): Promise<{ path: string; pid: number }> => response.json())),
      )
      expect(new Set(results.map((result) => result.path)).size).toBe(2)
      expect((yield* Effect.promise(() => fs.readdir(api.log))).toSorted()).toEqual(
        results.map((result) => path.basename(result.path)).toSorted(),
      )
      for (const result of results) {
        expect(result.pid).toBe(process.pid)
        expect(path.dirname(result.path)).toBe(api.log)
        expect(path.basename(result.path)).toStartWith(`heap-${process.pid}-`)
        if (process.platform !== "win32")
          expect((yield* Effect.promise(() => fs.stat(result.path))).mode & 0o777).toBe(0o600)
        const snapshot = yield* Effect.promise(() => Bun.file(result.path).json())
        expect(snapshot.snapshot.node_count).toBeGreaterThan(0)
        expect(snapshot.snapshot.meta.node_fields).toContain("self_size")
      }
    }),
  60_000,
)

it.live(
  "reports a failed write without blocking later snapshots",
  () =>
    Effect.gen(function* () {
      const root = yield* Effect.acquireDisposable(Effect.promise(() => tmpdir("opencode-heap-dump-")))
      const api = yield* server(root.path)
      // A file where the log directory should be makes the write fail.
      yield* Effect.promise(() => fs.rm(api.log, { recursive: true }))
      yield* Effect.promise(() => fs.writeFile(api.log, ""))

      const failed = yield* api.dump()
      expect(failed.status).toBe(500)
      expect(yield* Effect.promise(() => failed.json())).toMatchObject({
        _tag: "UnknownError",
        message: "Failed to write heap snapshot. Check server logs for details.",
        ref: expect.stringMatching(/^err_/),
      })

      yield* Effect.promise(() => fs.rm(api.log))
      const recovered = yield* api.dump()
      expect(recovered.status).toBe(200)
      const result: { path: string } = yield* Effect.promise(() => recovered.json())
      expect(yield* Effect.promise(() => Bun.file(result.path).exists())).toBe(true)
    }),
  30_000,
)
