import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "API Hub | Integrated System Documentation",
  description: "Technical instructions and API references for integrating with the ELYX system network.",
};

export default function ApiDocsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
