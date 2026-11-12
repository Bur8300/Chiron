import { useRef, useState } from "react";
import { Link, NavLink, Outlet } from "react-router";
import { Brand } from "../components/Brand";
import { Icon } from "../components/Icon";
import { tr } from "../i18n/tr";
import { pageRoutes, type Role } from "./routes";

export function AppShell({ role }: { role: Role }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const menuButton = useRef<HTMLButtonElement>(null);

  function closeMenu() {
    setMenuOpen(false);
    menuButton.current?.focus();
  }

  return (
    <div
      className="app-shell"
      onKeyDown={(event) => {
        if (event.key === "Escape" && menuOpen) closeMenu();
      }}
    >
      <a className="skip-link" href="#main-content">
        {tr.skip}
      </a>
      <aside className="sidebar">
        <div className="sidebar-top">
          <Link className="brand-link" to="/giris">
            <Brand />
          </Link>
          <button
            ref={menuButton}
            className="icon-button menu-toggle"
            aria-label={menuOpen ? tr.closeMenu : tr.openMenu}
            aria-expanded={menuOpen}
            aria-controls="workspace-navigation"
            onClick={() => setMenuOpen(!menuOpen)}
          >
            <Icon name={menuOpen ? "close" : "menu"} />
          </button>
        </div>
        <div
          className={`navigation-panel ${menuOpen ? "is-open" : ""}`}
          id="workspace-navigation"
        >
          <p className="nav-caption">{tr.navigation[role]}</p>
          <nav aria-label={tr.navigation[role]}>
            {pageRoutes
              .filter((route) => route.role === role)
              .map((route) => (
                <NavLink
                  key={route.path}
                  to={route.path}
                  className={({ isActive }) =>
                    `nav-link ${isActive ? "is-active" : ""}`
                  }
                >
                  <Icon name={route.icon} />
                  <span>{tr.pages[route.page].label}</span>
                </NavLink>
              ))}
          </nav>
          <div className="sidebar-note">
            <Icon name="book" />
            <p>{tr.tagline}</p>
            <span>{tr.roles[role]}</span>
          </div>
          <Link className="return-link" to="/giris">
            {tr.back}
            <Icon name="arrow" />
          </Link>
        </div>
      </aside>
      <div className="workspace-body">
        <header className="workspace-header">
          <span>{tr.workspace}</span>
          <span className="role-label">{tr.roles[role]}</span>
        </header>
        <div className="preview-banner">
          <span className="preview-badge">{tr.preview}</span>
          <p>{tr.previewNote}</p>
        </div>
        <main id="main-content" tabIndex={-1}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
