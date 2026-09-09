import { describe, expect, it } from "vitest";
import { displayValue, evidenceLabel } from "./presentation";

describe("honest value presentation", () => {
  it("does not turn absent data into a numeric placeholder", () => {
    expect(displayValue(null)).toBe("—");
    expect(displayValue(undefined)).toBe("—");
    expect(displayValue([])).toBe("—");
  });

  it("preserves zero and formats structured values", () => {
    expect(displayValue(0)).toBe("0");
    expect(displayValue(["email", "sms"])).toBe("email, sms");
    expect(evidenceLabel("canonical_operational_data")).toBe("canonical operational data");
  });
});
