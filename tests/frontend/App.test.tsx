import { cleanup, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router";
import { afterEach, describe, expect, test } from "vitest";

import App from "../../frontend/src/App";

afterEach(cleanup);

function open(path = "/") {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>,
  );
}

describe("public foundation preview", () => {
  test("offers preview access without claiming to authenticate a user", async () => {
    open();
    expect(
      screen.getByRole("heading", { name: "Öğrenmeye yer aç." }),
    ).toBeDefined();
    expect(screen.getByLabelText("Portal kimliği")).toBeDefined();
    expect(screen.getByLabelText("Şifre")).toBeDefined();
    expect(
      (screen.getByRole("button", { name: "Giriş yap" }) as HTMLButtonElement)
        .disabled,
    ).toBe(true);
    await userEvent.click(
      screen.getByRole("link", { name: "Öğrenci görünümünü incele" }),
    );
    expect(
      await screen.findByRole("heading", { name: "Derslerin, tek bir yerde." }),
    ).toBeDefined();
    expect(screen.getByText("Önizleme")).toBeDefined();
  });

  test("offers activation only for an existing portal account", async () => {
    open("/giris");
    await userEvent.click(
      screen.getByRole("link", { name: "Hesabını etkinleştir" }),
    );
    expect(
      await screen.findByRole("heading", { name: "İlk adım, hesabın." }),
    ).toBeDefined();
    expect(
      screen.getByText(/Yalnızca okul portalında kayıtlı hesaplar/),
    ).toBeDefined();
    expect(screen.queryByText("Kayıt ol")).toBeNull();
  });

  test.each([
    [
      "/onizleme/ogrenci/dersler",
      "Çalışma alanı",
      "Kaynaklarım",
      "Öğrenciler",
      "Hesap yönetimi",
    ],
    [
      "/onizleme/ogretmen/ogrenciler",
      "Öğretmen alanı",
      "Öğrenciler",
      "Kaynaklarım",
      "Hesap yönetimi",
    ],
    [
      "/onizleme/yonetici/ogrenciler",
      "Yönetici alanı",
      "Hesap yönetimi",
      "Kaynaklarım",
      "Çalışma planım",
    ],
  ])(
    "limits navigation in %s to the intended role",
    (path, label, present, absent, alsoAbsent) => {
      open(path);
      const nav = within(screen.getByRole("navigation", { name: label }));
      expect(nav.getByRole("link", { name: present })).toBeDefined();
      expect(nav.queryByRole("link", { name: absent })).toBeNull();
      expect(nav.queryByRole("link", { name: alsoAbsent })).toBeNull();
    },
  );

  test("supports direct links and focuses the heading after navigation", async () => {
    open("/onizleme/ogrenci/kaynaklar");
    expect(
      screen.getByRole("heading", { name: "Kaynaklarınla başla." }),
    ).toBeDefined();
    await userEvent.click(screen.getByRole("link", { name: "Soru sor" }));
    const heading = await screen.findByRole("heading", {
      name: "Merak ettiğini sor.",
    });
    expect(document.activeElement).toBe(heading);
    expect(document.title).toBe("Soru sor · Chiron");
    expect(
      screen
        .getByRole("link", { name: "Soru sor" })
        .getAttribute("aria-current"),
    ).toBe("page");
  });

  test("handles an unknown path with a recovery link", () => {
    open("/does-not-exist");
    expect(
      screen.getByRole("heading", { name: "Bu sayfayı bulamadık." }),
    ).toBeDefined();
    expect(
      screen.getByRole("link", { name: "Başlangıca dön" }).getAttribute("href"),
    ).toBe("/giris");
  });

  test("keeps the shell mounted while closing the menu after navigation", async () => {
    const user = userEvent.setup();
    open("/onizleme/ogrenci/dersler");
    const menuButton = screen.getByRole("button", { name: "Menüyü aç" });
    const navigation = screen.getByRole("navigation");
    await user.click(menuButton);
    expect(menuButton.getAttribute("aria-expanded")).toBe("true");
    await user.click(within(navigation).getByRole("link", { name: "Soru sor" }));
    expect(screen.getByRole("button", { name: "Menüyü aç" })).toBe(menuButton);
    expect(screen.getByRole("navigation")).toBe(navigation);
    expect(menuButton.getAttribute("aria-expanded")).toBe("false");
    expect(document.activeElement).toBe(screen.getByRole("heading", { level: 1 }));

    // Selecting the current route must also close the mobile disclosure.
    await user.click(menuButton);
    await user.click(within(navigation).getByRole("link", { name: "Soru sor" }));
    expect(menuButton.getAttribute("aria-expanded")).toBe("false");
  });
});
