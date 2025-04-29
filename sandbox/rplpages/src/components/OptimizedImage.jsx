import { useState } from 'react'

export default function OptimizedImage({ src, alt, ...props }) {
  const [loaded, setLoaded] = useState(false)

  return (
    <div className="relative">
      {!loaded && (
        <div className="absolute inset-0 bg-gray-200 animate-pulse rounded-lg" />
      )}
      <img
        src={src}
        alt={alt}
        loading="lazy"
        onLoad={() => setLoaded(true)}
        className={`${loaded ? 'opacity-100' : 'opacity-0'} transition-opacity duration-300`}
        {...props}
      />
    </div>
  )
}