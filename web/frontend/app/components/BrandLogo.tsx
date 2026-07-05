type BrandLogoProps = {
  size?: 'small' | 'large';
};

export function BrandLogo({ size = 'small' }: BrandLogoProps) {
  return (
    <img
      alt="Shandong Quantitative System logo"
      className={`brandLogo brandLogo-${size}`}
      src="/brand/shandong-quant-logo.png"
    />
  );
}
