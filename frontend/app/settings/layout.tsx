import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Core Configuration | System Settings",
  description: "Configure core operational parameters and system-wide settings for the ELYX platform.",
};

export default function SettingsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
