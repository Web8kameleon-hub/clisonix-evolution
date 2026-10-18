import assert from "node:assert/strict";
import { originMatches } from "../src/lib/security/request-origin.ts";

const internal = "http://clisonix-web:3000";
const canonical = "https://www.clisonix.com";
const forwarded = "https://www.clisonix.com";

assert.equal(originMatches(null, [internal, canonical]), true);
assert.equal(originMatches("https://www.clisonix.com", [internal, canonical]), true);
assert.equal(originMatches("https://www.clisonix.com/sign-up", [internal, forwarded]), true);
assert.equal(originMatches("https://clisonix.com", [internal, canonical]), false);
assert.equal(originMatches("https://attacker.example", [internal, canonical]), false);
assert.equal(originMatches("not-a-url", [internal, canonical]), false);
assert.equal(originMatches("https://www.clisonix.com.evil.example", [canonical]), false);

console.log("auth origin verification: 7/7 passed");
