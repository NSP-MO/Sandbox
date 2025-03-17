#include <iostream>
using namespace std;

class Base  {
public:
    Base()    { cout<<"A"; }
    ~Base()   { cout<<"B"; }
};

class Derived: public Base {
public:
    Derived()   { cout<<"C"; }
};

int main()  {
    Base *obj = new Derived();
    delete obj;
    return 0;
}
