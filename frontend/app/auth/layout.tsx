import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Secure Access | ELYX System Terminal",
  description: "Authenticate with the ELYX autonomous operations network. Secure system access verification.",
};

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
