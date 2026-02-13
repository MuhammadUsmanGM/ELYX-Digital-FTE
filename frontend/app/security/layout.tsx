import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Security Matrix | Advanced Causal Encryption",
  description: "Monitor neural security protocols and manage AES-256 vault encryption for the ELYX network.",
};

export default function SecurityLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
