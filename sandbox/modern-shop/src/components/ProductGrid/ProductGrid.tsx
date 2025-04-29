import { useInfiniteQuery } from '@tanstack/react-query';
import { useVirtualizer } from '@tanstack/react-virtual';
import ProductCard from '../ProductCard/ProductCard';
import Loader from '../Loader/Loader';
import './ProductGrid.css';

const fetchProducts = async ({ pageParam = 1 }) => {
  const response = await fetch(`/api/products?page=${pageParam}`);
  return response.json();
};

export default function ProductGrid() {
  const { 
    data, 
    isLoading, 
    fetchNextPage, 
    hasNextPage 
  } = useInfiniteQuery(['products'], fetchProducts, {
    getNextPageParam: (lastPage) => lastPage.nextPage,
  });

  const products = data?.pages.flatMap(page => page.products) || [];
  const parentRef = React.useRef<HTMLDivElement>(null);

  const rowVirtualizer = useVirtualizer({
    count: hasNextPage ? products.length + 1 : products.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 400,
    overscan: 5,
  });

  return (
    <div ref={parentRef} className="product-grid-container">
      <div
        className="product-grid"
        style={{
          height: `${rowVirtualizer.getTotalSize()}px`,
          width: '100%',
          position: 'relative',
        }}
      >
        {rowVirtualizer.getVirtualItems().map((virtualItem) => {
          const product = products[virtualItem.index];
          
          return product ? (
            <div
              key={virtualItem.key}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: `${virtualItem.size}px`,
                transform: `translateY(${virtualItem.start}px)`,
              }}
            >
              <ProductCard product={product} />
            </div>
          ) : (
            <div
              key={virtualItem.key}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: `${virtualItem.size}px`,
                transform: `translateY(${virtualItem.start}px)`,
              }}
            >
              <button 
                onClick={() => fetchNextPage()}
                className="load-more-button"
              >
                Load More
              </button>
            </div>
          );
        })}
      </div>
      
      {isLoading && <Loader />}
    </div>
  );
}