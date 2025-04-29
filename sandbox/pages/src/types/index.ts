export interface Product {
    id: string;
    name: string;
    price: number;
    discount?: number;
    rating: number;
    sold: number;
    image: string;
    description: string;
    category: string;
    stock: number;
  }
  
  export interface Category {
    id: string;
    name: string;
    icon: string;
  }