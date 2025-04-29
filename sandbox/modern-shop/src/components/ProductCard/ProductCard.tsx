import { motion } from 'framer-motion';
import { useRef } from 'react';
import { useCartStore } from '../../store/cartStore';
import { useHover, useMotionValue, useSpring, useTransform } from 'framer-motion';

interface ProductCardProps {
  product: Product;
}

export default function ProductCard({ product }: ProductCardProps) {
  const ref = useRef<HTMLDivElement>(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const isHovered = useHover(ref);
  
  const rotateX = useSpring(useTransform(y, [0, 400], [15, -15]), {
    stiffness: 300,
    damping: 20
  });
  
  const rotateY = useSpring(useTransform(x, [0, 400], [-15, 15]), {
    stiffness: 300,
    damping: 20
  });

  return (
    <motion.div
      ref={ref}
      style={{
        rotateX: isHovered ? rotateX : 0,
        rotateY: isHovered ? rotateY : 0,
        scale: isHovered ? 1.05 : 1,
      }}
      className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden relative group"
      whileHover={{ scale: 1.05 }}
      transition={{ type: 'spring', stiffness: 300 }}
    >
      <div className="relative aspect-square overflow-hidden">
        <img
          src={product.image}
          alt={product.name}
          className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
          loading="lazy"
        />
      </div>
      
      <div className="p-4 space-y-2">
        <h3 className="font-semibold text-lg truncate">{product.name}</h3>
        <div className="flex justify-between items-center">
          <span className="text-2xl font-bold text-primary">
            ${product.price}
          </span>
          <button 
            onClick={() => useCartStore.getState().addItem(product)}
            className="bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary-dark transition"
          >
            Add to Cart
          </button>
        </div>
      </div>
    </motion.div>
  );
}