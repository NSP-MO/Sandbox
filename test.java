class MyProgram
{
    public static void main(String[] args)
    {
        First obj1 =  new First();
        Second obj2 =  new Second();

        First ref = new First();
        ref = obj1;
        ref.display();

        ref = obj2;
        ref.display();

        System.out.println();
    }
}