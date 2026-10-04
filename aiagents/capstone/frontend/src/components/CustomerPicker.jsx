import { CUSTOMERS } from "../lib/customers.js";

export default function CustomerPicker({ value, onChange }) {
  return (
    <fieldset className="flex flex-col gap-2">
      <legend className="mb-2 text-sm font-medium text-ink-100">Customer</legend>

      {CUSTOMERS.map((customer) => {
        const selected = customer.id === value;

        return (
          <label
            key={customer.id}
            className={`flex cursor-pointer items-start gap-3 rounded-xl border px-3 py-2.5 transition-colors ${
              selected ? "border-signal-dim bg-ink-800" : "border-ink-700 bg-ink-900 hover:border-ink-500"
            }`}
          >
            <input
              type="radio"
              name="customer"
              value={customer.id}
              checked={selected}
              onChange={() => onChange(customer.id)}
              className="mt-1 accent-[var(--color-signal)]"
            />
            <span className="flex flex-col">
              <span className="text-sm text-ink-100">{customer.name}</span>
              <span className="text-xs leading-snug text-ink-300">{customer.scenario}</span>
            </span>
          </label>
        );
      })}
    </fieldset>
  );
}
