export type DisplayValue = string | number | boolean | null | string[];

export function displayValue(value: DisplayValue | undefined): string {
  if (value === null || value === undefined || value === "") return "—";
  if (Array.isArray(value)) return value.length ? value.join(", ") : "—";
  return String(value).replaceAll("_", " ");
}

export function evidenceLabel(value: string): string {
  return value.replaceAll("_", " ");
}
