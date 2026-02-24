import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Data Privacy Protocol | ELYX Security Standards",
  description: "Advanced data encryption and privacy protocols for autonomous business operations.",
};

export default function PrivacyLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
