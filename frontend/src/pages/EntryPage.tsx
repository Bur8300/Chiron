import { Link } from "react-router";
import { roleHome, type Role } from "../app/routes";
import { Brand } from "../components/Brand";
import { Field } from "../components/Field";
import { Icon } from "../components/Icon";
import { tr } from "../i18n/tr";

export function EntryPage({ activate = false }: { activate?: boolean }) {
  const copy = tr.login;
  return (
    <div className="entry-page">
      <a className="skip-link" href="#main-content">
        {tr.skip}
      </a>
      <header className="entry-header">
        <Link className="brand-link" to="/giris">
          <Brand />
        </Link>
        <span className="preview-badge">{tr.preview}</span>
      </header>
      <main id="main-content" tabIndex={-1} className="entry-main">
        <section className="entry-intro">
          <p className="eyebrow">{copy.eyebrow}</p>
          <h1 tabIndex={-1}>{activate ? copy.activateTitle : copy.title}</h1>
          <p className="entry-description">
            {activate ? copy.activateNote : copy.intro}
          </p>
          <div className="entry-benefits">
            <div>
              <Icon name="chat" />
              <h2>{copy.sources}</h2>
              <p>{copy.sourcesNote}</p>
            </div>
            <div>
              <Icon name="calendar" />
              <h2>{copy.pace}</h2>
              <p>{copy.paceNote}</p>
            </div>
          </div>
        </section>
        <section className="entry-card" aria-labelledby="entry-form-title">
          <span className="form-emblem">
            <Icon name="book" />
          </span>
          <h2 id="entry-form-title">
            {activate ? copy.activate : copy.panelTitle}
          </h2>
          <p>{copy.panelNote}</p>
          <div className="entry-fields">
            <Field
              id="portal-id"
              name="username"
              label={copy.portalId}
              autoComplete="username"
              disabled
            />
            <Field
              id="password"
              name="password"
              label={activate ? copy.newPassword : copy.password}
              type="password"
              autoComplete={activate ? "new-password" : "current-password"}
              disabled
            />
          </div>
          <button
            className="primary-button"
            disabled
            aria-describedby="entry-unavailable"
          >
            {activate ? copy.activate : copy.submit}
            <Icon name="arrow" />
          </button>
          <p className="entry-notice" id="entry-unavailable">
            {copy.unavailable}
          </p>
          <p className="entry-switch">
            {activate ? copy.existing : copy.firstTime}{" "}
            <Link to={activate ? "/giris" : "/hesap-etkinlestir"}>
              {activate ? copy.returnToLogin : copy.activate}
            </Link>
          </p>
        </section>
        <section className="preview-links" aria-labelledby="preview-title">
          <h2 id="preview-title">{copy.lookAround}</h2>
          <div>
            {(["student", "teacher", "admin"] as Role[]).map((role) => (
              <Link key={role} to={roleHome[role]}>
                {tr.previews[role]}
                <Icon name="arrow" />
              </Link>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
