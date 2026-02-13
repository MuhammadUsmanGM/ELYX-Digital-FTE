import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Communication Bridge | Unified Relay Node",
  description: "Unified communication management across email, Slack, and other strategic channels.",
};

export default function CommsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
