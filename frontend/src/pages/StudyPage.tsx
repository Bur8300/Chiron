import { Link } from "react-router";
import { pageRoutes, type PageRoute } from "../app/routes";
import { EmptyState } from "../components/EmptyState";
import { Icon } from "../components/Icon";
import { tr } from "../i18n/tr";

export function StudyPage({ route }: { route: PageRoute }) {
  const copy = tr.pages[route.page];
  const shortcuts = pageRoutes
    .filter((item) => item.role === route.role && item.page !== route.page)
    .slice(0, 3);
  return (
    <div className="page-content">
      <div className="page-heading">
        <h1 tabIndex={-1}>{copy.title}</h1>
        <p className="page-description">{copy.description}</p>
      </div>
      <EmptyState title={copy.empty} description={copy.hint} />
      {shortcuts.length > 0 && (
        <section className="next-section" aria-labelledby="next-heading">
          <div className="section-heading">
            <h2 id="next-heading">{tr.explore}</h2>
            <p>{tr.exploreNote}</p>
          </div>
          <div className="shortcut-list">
            {shortcuts.map((item) => (
              <Link className="shortcut-card" key={item.path} to={item.path}>
                <span className="shortcut-icon">
                  <Icon name={item.icon} />
                </span>
                <div className="shortcut-copy">
                  <h3>{tr.pages[item.page].label}</h3>
                  <p>{tr.pages[item.page].description}</p>
                </div>
                <span className="card-action">
                  {tr.open}
                  <Icon name="arrow" />
                </span>
              </Link>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
