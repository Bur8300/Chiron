import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, expect, test } from "vitest";
import { Field } from "../../frontend/src/components/Field";

afterEach(cleanup);

test("connects a field to its label, hint and error", () => {
  render(
    <Field
      id="example"
      label="Portal kimliği"
      hint="Okul portalındaki kimlik."
      error="Kimliğini kontrol et."
    />,
  );
  const input = screen.getByLabelText("Portal kimliği");
  expect(input.getAttribute("aria-invalid")).toBe("true");
  expect(input.getAttribute("aria-describedby")).toBe(
    "example-hint example-error",
  );
  expect(screen.getByRole("alert").textContent).toBe("Kimliğini kontrol et.");
});
