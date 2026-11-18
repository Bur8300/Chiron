import { tr } from "../i18n/tr";
import { Icon } from "./Icon";

export function Brand() {
  return (
    <span className="brand">
      <span className="brand-mark">
        <Icon name="book" />
      </span>
      <span>
        {tr.brand}
        <small>{tr.tagline}</small>
      </span>
    </span>
  );
}
