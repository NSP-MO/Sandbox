import { useInfiniteQuery } from '@tanstack/react-query';

const fetchProducts = async ({ pageParam = 1 }) => {
  const response = await fetch(`/api/products?page=${pageParam}`);
  return response.json();
};

export const useProducts = () => {
  return useInfiniteQuery({
    queryKey: ['products'],
    queryFn: fetchProducts,
    getNextPageParam: (lastPage) => lastPage.nextPage,
    staleTime: 1000 * 60 * 5, // 5 minutes
    cacheTime: 1000 * 60 * 30, // 30 minutes
  });
};