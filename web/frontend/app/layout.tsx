import './styles.css';

export const metadata = {
  title: 'Shandong SaaS',
  description: 'Production SaaS architecture shell',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
