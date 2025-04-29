export interface Product {
    id: string;
    name: string;
    price: number;
    description: string;
    image: string;
    category: string;
    rating: number;
    stock: number;
  }
  
  export const fetchProducts = async ({ pageParam = 1 }): Promise<{
    products: Product[];
    nextPage: number | null;
  }> => {
    // Mock API response
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const mockProducts: Product[] = Array.from({ length: 20 }).map((_, i) => ({
      id: `${pageParam}-${i}`,
      name: `Product ${pageParam}-${i}`,
      price: Math.random() * 100 + 20,
      description: `Premium quality product ${i} with advanced features`,
      image: `https://picsum.photos/200?random=${pageParam}-${i}`,
      category: ['electronics', 'clothing', 'home'][Math.floor(Math.random() * 3)],
      rating: Math.random() * 3 + 2,
      stock: Math.floor(Math.random() * 50) + 10
    }));
  
    return {
      products: mockProducts,
      nextPage: pageParam < 3 ? pageParam + 1 : null
    };
  };