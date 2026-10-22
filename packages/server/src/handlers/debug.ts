import { LocationServiceMap } from "@opencode/core/location-service-map"
import { UnknownError } from "@opencode/protocol/errors"
import { Global } from "@opencode/util/global"
import { HeapSnapshot } from "@opencode/util/heap-snapshot"
import { Effect, Option, RcMap } from "effect"
import { HttpApiBuilder } from "effect/http-api"
import { Api } from "../api"
import { requestRef } from "../location"

export const DebugHandler = HttpApiBuilder.group(Api, "server.debug", (handlers) =>
  Effect.gen(function* () {
    const global = yield* Global.Service
    return handlers
      .handle(
        "debug.heapDump",
        Effect.fn("server.debug.heapDump")(function* () {
          return yield* HeapSnapshot.write(global.log).pipe(
            Effect.catch((cause) => {
              const ref = `err_${crypto.randomUUID().slice(0, 8)}`
              return Effect.logError("failed to write heap snapshot", { cause }).pipe(
                Effect.annotateLogs({ ref }),
                Effect.andThen(
                  Effect.fail(
                    new UnknownError({ message: "Failed to write heap snapshot. Check server logs for details.", ref }),
                  ),
                ),
              )
            }),
          )
        }),
      )
      .handle(
        "debug.location",
        Effect.fn(function* () {
          const locations = Option.getOrThrow(yield* Effect.serviceOption(LocationServiceMap.Service))
          return Array.from(yield* RcMap.keys(locations.rcMap))
        }),
      )
      .handle(
        "debug.location.evict",
        Effect.fn(function* (ctx) {
          const locations = Option.getOrThrow(yield* Effect.serviceOption(LocationServiceMap.Service))
          // Resolve through requestRef so the key matches the shape the location
          // middleware cached the services under.
          yield* locations.invalidate(requestRef(ctx.request))
        }),
      )
  }),
)
