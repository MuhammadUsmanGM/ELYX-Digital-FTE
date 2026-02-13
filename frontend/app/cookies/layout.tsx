import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Cookie Directive | Data Persistence Protocols",
  description: "Review the protocols for data persistence and browser cookies within the ELYX network.",
};

export default function CookiesLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
