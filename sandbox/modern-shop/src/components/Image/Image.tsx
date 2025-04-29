import { useState } from 'react';
import { LazyLoadImage } from 'react-lazy-load-image-component';

interface ImageProps {
  src: string;
  alt: string;
  className?: string;
}

export default function Image({ src, alt, className }: ImageProps) {
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState(false);

  return (
    <div className={`relative ${className}`}>
      {!loaded && !error && (
        <div className="absolute inset-0 bg-gray-100 animate-pulse" />
      )}
      
      <LazyLoadImage
        src={error ? '/placeholder.jpg' : src}
        alt={alt}
        className={`w-full h-full object-cover transition-opacity ${
          loaded ? 'opacity-100' : 'opacity-0'
        }`}
        afterLoad={() => setLoaded(true)}
        onError={() => setError(true)}
        effect="blur"
      />
    </div>
  );
}