import { ClientError, OpenCode } from "@opencode/client"
import { Service } from "@opencode/client/effect/service"
import { Effect, Option, Predicate } from "effect"
import { EOL } from "node:os"
import { Commands } from "../../commands"
import { Runtime } from "../../../framework/runtime"
import { ServerConnection } from "../../../services/server-connection"
import { ServiceConfig } from "../../../services/service-config"
import { errorMessage } from "../../../util/error"

const handler = Effect.fn("cli.debug.heap-dump")(function* (
  input: Runtime.Input<(typeof Commands.commands.debug.commands)["heap-dump"]>,
) {
  const endpoint = yield* running(Option.getOrUndefined(input.server))
  const client = OpenCode.make({ baseUrl: endpoint.url, headers: Service.headers(endpoint) })
  const snapshot = yield* Effect.tryPromise({
    try: (signal) => client.debug.heapDump({ signal }),
    catch: (cause) =>
      cause instanceof ClientError &&
      cause.reason === "UnexpectedStatus" &&
      Predicate.hasProperty(cause.cause, "status") &&
      cause.cause.status === 404
        ? new Error(`The server at ${endpoint.url} does not support heap dumps. Update and restart it first.`)
        : cause,
  })
  process.stdout.write(snapshot.path + EOL)
})

export default Runtime.handler(Commands.commands.debug.commands["heap-dump"], (input) =>
  handler(input).pipe(
    Effect.catch((error) =>
      Effect.sync(() => {
        process.stderr.write(errorMessage(error) + EOL)
        process.exitCode = 1
      }),
    ),
  ),
)

// A fresh server has nothing worth capturing, so only an already-running one is used: never start,
// replace, or restart the background service.
const running = Effect.fnUntraced(function* (server: string | undefined) {
  if (server !== undefined) return (yield* ServerConnection.resolve({ server })).endpoint
  const options = yield* ServiceConfig.options()
  const endpoint = yield* Service.discover({ ...options, version: undefined })
  if (endpoint) return endpoint
  return yield* Effect.fail(
    new Error("No background server is running. Pass --server <url> to capture a server started another way."),
  )
})
