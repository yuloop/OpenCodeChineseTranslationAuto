import { describe, expect, test } from "bun:test"
import { route } from "../src/lib/language"

describe("language.route", () => {
  test("keeps the changelog unprefixed for every locale", () => {
    expect(route("de", "/changelog")).toBe("/changelog")
    expect(route("zh", "/zh/changelog")).toBe("/changelog")
  })

  test("prefixes other marketing pages", () => {
    expect(route("de", "/download")).toBe("/de/download")
  })
})
