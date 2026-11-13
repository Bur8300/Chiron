import { useEffect } from "react";
import { Link, Navigate, Route, Routes, useLocation } from "react-router";
import { AppShell } from "./app/AppShell";
import { pageRoutes, type Role } from "./app/routes";
import { tr } from "./i18n/tr";
import { EntryPage } from "./pages/EntryPage";
import { StudyPage } from "./pages/StudyPage";

export default function App() {
  const { pathname } = useLocation();
  useEffect(() => {
    const route = pageRoutes.find((item) => item.path === pathname);
    const title = route
      ? tr.pages[route.page].label
      : pathname === "/hesap-etkinlestir"
        ? tr.login.activate
        : pathname === "/giris" || pathname === "/"
          ? tr.login.submit
          : tr.notFound.title;
    document.title = `${title} · ${tr.brand}`;
    // Put keyboard and screen reader users at the start of the new page.
    document.querySelector<HTMLElement>("h1")?.focus({ preventScroll: true });
    window.scrollTo?.(0, 0);
  }, [pathname]);

  return (
    <Routes>
      <Route path="/" element={<Navigate to="/giris" replace />} />
      <Route path="/giris" element={<EntryPage />} />
      <Route path="/hesap-etkinlestir" element={<EntryPage activate />} />
      {(["student", "teacher", "admin"] as Role[]).map((role) => (
        <Route key={role} element={<AppShell role={role} />}>
          {pageRoutes
            .filter((route) => route.role === role)
            .map((route) => (
              <Route
                key={route.path}
                path={route.path}
                element={<StudyPage route={route} />}
              />
            ))}
        </Route>
      ))}
      <Route
        path="*"
        element={
          <main id="main-content" className="not-found">
            <p className="eyebrow">{tr.brand}</p>
            <h1 tabIndex={-1}>{tr.notFound.title}</h1>
            <p>{tr.notFound.description}</p>
            <Link className="primary-button" to="/giris">
              {tr.notFound.action}
            </Link>
          </main>
        }
      />
    </Routes>
  );
}
