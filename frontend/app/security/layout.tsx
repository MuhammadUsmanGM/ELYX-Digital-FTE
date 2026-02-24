import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Security Shield | Enterprise Encryption",
  description: "Monitor system security protocols and manage AES-256 vault encryption for the ELYX platform.",
};

export default function SecurityLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
