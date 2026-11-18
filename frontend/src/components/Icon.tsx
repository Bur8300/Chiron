type IconName =
  | "book"
  | "folder"
  | "chat"
  | "file"
  | "quiz"
  | "calendar"
  | "users"
  | "arrow"
  | "menu"
  | "close";

const paths: Record<IconName, string> = {
  book: "M12 6c-3-2-6-2-9-1v14c3-1 6-1 9 1m0-14c3-2 6-2 9-1v14c-3-1-6-1-9 1V6",
  folder: "M3 7V5h6l2 3h10v12H3V7Z",
  chat: "M4 4h16v12H9l-5 4V4Zm4 5h8m-8 3h5",
  file: "M6 3h8l4 4v14H6V3Zm8 0v5h4M9 12h6m-6 4h6",
  quiz: "M8 4H5v17h14V4h-3M8 3h8v4H8V3Zm0 11 3 3 5-6",
  calendar: "M4 5h16v16H4V5Zm4-3v6m8-6v6M4 11h16m-12 4h2m4 0h2",
  users:
    "M16 21v-3a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v3m20 0v-3a4 4 0 0 0-3-4M9 3a4 4 0 1 0 0 8 4 4 0 0 0 0-8Zm8 0a4 4 0 0 1 0 8",
  arrow: "M4 12h16m-6-6 6 6-6 6",
  menu: "M4 6h16M4 12h16M4 18h16",
  close: "m6 6 12 12M6 18 18 6",
};

export function Icon({
  name,
  className = "",
}: {
  name: IconName;
  className?: string;
}) {
  return (
    <svg
      className={`icon ${className}`}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d={paths[name]} />
    </svg>
  );
}
