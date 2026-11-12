import { tr } from "../i18n/tr";

export type Role = "student" | "teacher" | "admin";
export type PageId = keyof typeof tr.pages;
export type PageRoute = {
  path: string;
  page: PageId;
  role: Role;
  icon: "book" | "folder" | "chat" | "file" | "quiz" | "calendar" | "users";
};

// These routes contain public empty previews, never authenticated student data.
export const pageRoutes: PageRoute[] = [
  {
    path: "/onizleme/ogrenci/dersler",
    page: "courses",
    role: "student",
    icon: "book",
  },
  {
    path: "/onizleme/ogrenci/kaynaklar",
    page: "sources",
    role: "student",
    icon: "folder",
  },
  {
    path: "/onizleme/ogrenci/soru-cevap",
    page: "questions",
    role: "student",
    icon: "chat",
  },
  {
    path: "/onizleme/ogrenci/ozetler",
    page: "summaries",
    role: "student",
    icon: "file",
  },
  {
    path: "/onizleme/ogrenci/sinavlar",
    page: "quizzes",
    role: "student",
    icon: "quiz",
  },
  {
    path: "/onizleme/ogrenci/calisma-plani",
    page: "planner",
    role: "student",
    icon: "calendar",
  },
  {
    path: "/onizleme/ogretmen/ogrenciler",
    page: "teacher",
    role: "teacher",
    icon: "users",
  },
  {
    path: "/onizleme/yonetici/ogrenciler",
    page: "admin",
    role: "admin",
    icon: "users",
  },
  {
    path: "/onizleme/yonetici/hesaplar",
    page: "accounts",
    role: "admin",
    icon: "users",
  },
];

export const roleHome: Record<Role, string> = {
  student: "/onizleme/ogrenci/dersler",
  teacher: "/onizleme/ogretmen/ogrenciler",
  admin: "/onizleme/yonetici/ogrenciler",
};
