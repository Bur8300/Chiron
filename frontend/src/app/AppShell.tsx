import { useEffect, useRef, useState } from "react";
import { Link, NavLink, Outlet, useLocation } from "react-router";
import { Brand } from "../components/Brand";
import { Icon } from "../components/Icon";
import { tr } from "../i18n/tr";
import { pageRoutes, type Role } from "./routes";

export function AppShell({ role }: { role: Role }) {
  const location = useLocation();
  const [menu, setMenu] = useState({ locationKey: location.key, open: false });
  const menuButton = useRef<HTMLButtonElement>(null);

  // Reset only the disclosure on navigation, including browser history changes.
  if (menu.locationKey !== location.key) {
    setMenu({ locationKey: location.key, open: false });
  }
  const menuOpen = menu.locationKey === location.key && menu.open;

  function setMenuOpen(open: boolean) {
    setMenu({ locationKey: location.key, open });
  }

  useEffect(() => {
    // A same-page link also closes the menu. Do not leave focus in hidden navigation.
    document.querySelector<HTMLElement>("h1")?.focus({ preventScroll: true });
  }, [location.key]);

  function closeMenu() {
    setMenuOpen(false);
    menuButton.current?.focus();
  }

  return (
    <div
      className="app-shell min-h-dvh min-[761px]:grid min-[761px]:grid-cols-[224px_minmax(0,1fr)] min-[1101px]:grid-cols-[248px_minmax(0,1fr)]"
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
                    `nav-link flex items-center gap-3 ${isActive ? "is-active" : ""}`
                  }
                >
                  <Icon name={route.icon} />
                  <span>{tr.pages[route.page].label}</span>
                </NavLink>
              ))}
          </nav>
          <div className="sidebar-note">
            <Icon name="book" />
            <p>{role === "student" ? tr.tagline : tr.staff.tagline}</p>
            <span>{tr.roles[role]}</span>
          </div>
          <Link className="return-link" to="/giris">
            {tr.back}
            <Icon name="arrow" />
          </Link>
        </div>
      </aside>
      <div className="workspace-body min-w-0">
        <header className="workspace-header flex items-center justify-between gap-4">
          <span>{role === "student" ? tr.workspace : tr.navigation[role]}</span>
          <span className="role-label">{tr.roles[role]}</span>
        </header>
        <div className="preview-banner">
          <span className="preview-badge">{tr.preview}</span>
          <p>{role === "student" ? tr.previewNote : tr.staff.previewNote}</p>
        </div>
        <main id="main-content" tabIndex={-1}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
