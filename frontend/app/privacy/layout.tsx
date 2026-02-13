import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Neural Privacy Protocol | ELYX Security Matrix",
  description: "Advanced data encryption and privacy protocols for autonomous business intelligence.",
};

export default function PrivacyLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
