import type { ReactNode } from "react";
import { Icon } from "./Icon";

export function EmptyState({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children?: ReactNode;
}) {
  return (
    <section className="empty-state">
      <div className="empty-art" aria-hidden="true">
        <Icon name="book" />
      </div>
      <div className="empty-copy">
        <h2>{title}</h2>
        <p>{description}</p>
        {children}
      </div>
    </section>
  );
}
