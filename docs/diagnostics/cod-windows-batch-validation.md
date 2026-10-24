# Windows installer batch fixture validation

Source: c477bb93db0120490d4cee382702227dd9d76061. Device: the authorized GamingLaptop, using real Windows cmd.exe.

The unchanged tests/host/check-dock-installers.py compiled the production DockInstallers.swift fixture under Swift6.4.1 and AddressSanitizer. External temporary-directory cleanup instrumentation exported its generated fixture.cmd; no source or assertions were changed. Template SHA256:

`3c561623ba91d7f4b9672a5d9c634365413aac5f44885f7a5e4a97a9ad9ba5e7`

The fixture ran in a newly created Windows user Temp directory whose name contains spaces. Only four stand-in CMD files were created, returning0,-9,3010,1603. The service command deliberately named a nonexistent executable. Actual ledger:

```text
begin 4
services failed
start 1 ok
exit 1 0
start 2 negative
exit 2 -9
start 3 restart
exit 3 3010
start 4 fails
exit 4 1603
end
```

The exact expected ledger comparison passed. The batch process returned1603, preserving its final stand-in failure. Instantiated batch SHA256: `a3bfb391c2663bc44f209abf8808db43bf9e3382bd1215492f94875b512f0859`. Ledger SHA256: `aace26f823389264e85c5619dae60b4b5dbe771cfc6929cf62f540c9c2f08a31`.

This verifies the generated batch's signed status reporting and simulated service-failure path on Windows. No real game, prerequisite installer, Dockhost, driver or service was executed. No security setting or existing installation was changed. The optional staged ARM64EC Dockhost service-connection check, iOS launch and Call of Duty startup remain untested. Fixture files remain isolated in the new Temp directory for review.
