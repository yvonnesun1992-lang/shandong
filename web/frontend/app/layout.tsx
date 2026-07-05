import './styles.css';

export const metadata = {
  title: 'Shandong Quantitative System',
  description: 'Institutional-grade local-first quant platform',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
