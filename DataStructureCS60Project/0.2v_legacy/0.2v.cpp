#include <iostream>
#include <fstream>
#include <string>
#include <ctime>
#include <unordered_map>
using namespace std;

struct Applicant {
    string id;
    string name;
    string address;
    string region;
    time_t submissionTime;
    string status;
    Applicant* next;
    Applicant* prev;
};

class KtpSystem {
private:
    Applicant* head;
    Applicant* tail;
    unordered_map<string, Applicant*> idMap;
    Applicant* revisionStackTop;

    string generateId(const string& region) {
        return region + "-" + to_string(time(nullptr));
    }

public:
    KtpSystem() : head(nullptr), tail(nullptr), revisionStackTop(nullptr) {}

    ~KtpSystem() {
        // Cleanup memory
        Applicant* current = head;
        while (current) {
            Applicant* next = current->next;
            delete current;
            current = next;
        }
    }

    void submitApplication(const string& name, const string& address, const string& region) {
        Applicant* newApp = new Applicant{
            generateId(region),
            name,
            address,
            region,
            time(nullptr),
            "pending",
            nullptr,
            nullptr
        };

        // Add to main list
        if (!head) {
            head = tail = newApp;
        } else {
            tail->next = newApp;
            newApp->prev = tail;
            tail = newApp;
        }

        // Add to verification queue
        idMap[newApp->id] = newApp;
        saveToFile();
    }

    void processVerification() {
        if (!head) return;

        Applicant* toProcess = head;
        head = head->next;
        if (head) head->prev = nullptr;
        else tail = nullptr;

        toProcess->status = "verified";
        idMap.erase(toProcess->id);
        delete toProcess;
        saveToFile();
    }

    void editApplication(const string& id, const string& newName, 
                       const string& newAddress, const string& newRegion) {
        if (idMap.find(id) == idMap.end()) return;

        Applicant* app = idMap[id];
        
        // Push to revision stack
        Applicant* revision = new Applicant(*app);
        revision->next = revisionStackTop;
        revisionStackTop = revision;

        // Update application
        app->name = newName;
        app->address = newAddress;
        app->region = newRegion;
        app->status = "revision";
        saveToFile();
    }

    void undoRevision(const string& id) {
        if (idMap.find(id) == idMap.end() || !revisionStackTop) return;

        Applicant* current = idMap[id];
        Applicant* revision = revisionStackTop;
        revisionStackTop = revisionStackTop->next;

        // Restore from revision
        current->name = revision->name;
        current->address = revision->address;
        current->region = revision->region;
        current->status = "pending";
        
        delete revision;
        saveToFile();
    }

    void sortByRegion() {
        // Bubble sort implementation for linked list
        bool swapped;
        do {
            swapped = false;
            Applicant** ptr = &head;
            
            while ((*ptr)->next) {
                Applicant* a = *ptr;
                Applicant* b = a->next;
                
                if (a->region > b->region) {
                    a->next = b->next;
                    b->prev = a->prev;
                    a->prev = b;
                    b->next = a;
                    
                    if (b->prev)
                        b->prev->next = b;
                    else
                        head = b;
                    
                    if (a->next)
                        a->next->prev = a;
                    
                    swapped = true;
                }
                ptr = &(*ptr)->next;
            }
        } while (swapped);
    }

    void sortByTime() {
        // Bubble sort implementation for linked list
        bool swapped;
        do {
            swapped = false;
            Applicant** ptr = &head;
            
            while ((*ptr)->next) {
                Applicant* a = *ptr;
                Applicant* b = a->next;
                
                if (a->submissionTime > b->submissionTime) {
                    a->next = b->next;
                    b->prev = a->prev;
                    a->prev = b;
                    b->next = a;
                    
                    if (b->prev)
                        b->prev->next = b;
                    else
                        head = b;
                    
                    if (a->next)
                        a->next->prev = a;
                    
                    swapped = true;
                }
                ptr = &(*ptr)->next;
            }
        } while (swapped);
    }

    void displayQueue() {
        Applicant* current = head;
        int position = 1;
        while (current) {
            cout << position++ << ". ID: " << current->id 
                 << "\n   Name: " << current->name
                 << "\n   Region: " << current->region
                 << "\n   Status: " << current->status
                 << "\n   Submitted: " << ctime(&current->submissionTime)
                 << "----------------------------------------\n";
            current = current->next;
        }
    }

    void saveToFile() {
        ofstream file("ktp_data.txt");
        Applicant* current = head;
        while (current) {
            file << current->id << "\n"
                 << current->name << "\n"
                 << current->address << "\n"
                 << current->region << "\n"
                 << current->submissionTime << "\n"
                 << current->status << "\n";
            current = current->next;
        }
    }

    void loadFromFile() {
        ifstream file("ktp_data.txt");
        string line;
        
        while (getline(file, line)) {
            Applicant* app = new Applicant();
            app->id = line;
            
            getline(file, app->name);
            getline(file, app->address);
            getline(file, app->region);
            
            file >> app->submissionTime;
            file.ignore();
            
            getline(file, app->status);
            
            // Add to linked list
            if (!head) {
                head = tail = app;
            } else {
                tail->next = app;
                app->prev = tail;
                tail = app;
            }
            
            idMap[app->id] = app;
        }
    }
};

int main() {
    KtpSystem system;
    system.loadFromFile();

    while (true) {
        cout << "\n=== KTP Management System ==="
             << "\n1. Submit New Application"
             << "\n2. Process Verification"
             << "\n3. Sort by Region"
             << "\n4. Sort by Submission Time"
             << "\n5. Edit Application"
             << "\n6. Undo Revision"
             << "\n7. Show Queue"
             << "\n8. Exit"
             << "\nEnter choice: ";

        int choice;
        cin >> choice;
        cin.ignore();

        if (choice == 8) break;

        string id, name, address, region;
        
        switch (choice) {
            case 1:
                cout << "Enter name: ";
                getline(cin, name);
                cout << "Enter address: ";
                getline(cin, address);
                cout << "Enter region: ";
                getline(cin, region);
                system.submitApplication(name, address, region);
                break;
                
            case 2:
                system.processVerification();
                break;
                
            case 3:
                system.sortByRegion();
                break;
                
            case 4:
                system.sortByTime();
                break;
                
            case 5:
                cout << "Enter application ID: ";
                getline(cin, id);
                cout << "Enter new name: ";
                getline(cin, name);
                cout << "Enter new address: ";
                getline(cin, address);
                cout << "Enter new region: ";
                getline(cin, region);
                system.editApplication(id, name, address, region);
                break;
                
            case 6:
                cout << "Enter application ID: ";
                getline(cin, id);
                system.undoRevision(id);
                break;
                
            case 7:
                system.displayQueue();
                break;
        }
    }

    return 0;
}