import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Business Intelligence | Strategic Growth Hub",
  description: "Advanced analytics and strategic growth vectors for modern autonomous enterprises.",
};

export default function BusinessLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
