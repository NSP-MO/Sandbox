#include <iostream>
#include <string>
#include <ctime>
#include <unordered_map>
#include <windows.h>
#include <sql.h>
#include <sqlext.h>

using namespace std;

struct Applicant {
    string id;
    string name;
    string address;
    string region;
    time_t submissionTime;
    string status;
    Applicant* next = nullptr;
    Applicant* prev = nullptr;
};

class KtpSystem {
private:
    Applicant* head;
    Applicant* tail;
    unordered_map<string, Applicant*> idMap;
    Applicant* revisionStackTop;

    // ODBC handles
    SQLHENV hEnv;
    SQLHDBC hDbc;

    // Helper: Generate unique ID
    string generateId(const string& region) {
        return region + "-" + to_string(time(nullptr));
    }

    // Helper: Execute a SQL query (simple version)
    bool executeSQL(const string &query) {
        SQLHSTMT hStmt;
        SQLRETURN ret = SQLAllocHandle(SQL_HANDLE_STMT, hDbc, &hStmt);
        ret = SQLExecDirect(hStmt, (SQLCHAR*)query.c_str(), SQL_NTS);
        SQLFreeHandle(SQL_HANDLE_STMT, hStmt);
        return SQL_SUCCEEDED(ret);
    }

    // Connect to Azure SQL using ODBC
    void connectToDB() {
        SQLRETURN ret;
        ret = SQLAllocHandle(SQL_HANDLE_ENV, SQL_NULL_HANDLE, &hEnv);
        ret = SQLSetEnvAttr(hEnv, SQL_ATTR_ODBC_VERSION, (SQLPOINTER)SQL_OV_ODBC3, 0);
        ret = SQLAllocHandle(SQL_HANDLE_DBC, hEnv, &hDbc);
        
        // Update the following connection string with your actual Azure SQL credentials
        SQLCHAR connStr[] = "Driver={ODBC Driver 17 for SQL Server};Server=tcp:yourserver.database.windows.net,1433;"
                            "Database=yourdatabase;Uid=yourusername;Pwd=yourpassword;"
                            "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;";
        ret = SQLDriverConnect(hDbc, NULL, connStr, SQL_NTS, NULL, 0, NULL, SQL_DRIVER_COMPLETE);
        if(SQL_SUCCEEDED(ret)) {
            cout << "Connected to Azure SQL successfully.\n";
        } else {
            cout << "Failed to connect to Azure SQL.\n";
        }
    }

    void disconnectFromDB() {
        SQLDisconnect(hDbc);
        SQLFreeHandle(SQL_HANDLE_DBC, hDbc);
        SQLFreeHandle(SQL_HANDLE_ENV, hEnv);
    }

    // Load data from the Azure SQL database into the linked list
    void loadFromDB() {
        string query = "SELECT id, name, address, region, submissionTime, status FROM Applicants";
        SQLHSTMT hStmt;
        SQLRETURN ret = SQLAllocHandle(SQL_HANDLE_STMT, hDbc, &hStmt);
        ret = SQLExecDirect(hStmt, (SQLCHAR*)query.c_str(), SQL_NTS);

        while(SQLFetch(hStmt) == SQL_SUCCESS) {
            char id[256], name[256], address[256], region[256], status[256];
            long submissionTime;
            SQLGetData(hStmt, 1, SQL_C_CHAR, id, sizeof(id), NULL);
            SQLGetData(hStmt, 2, SQL_C_CHAR, name, sizeof(name), NULL);
            SQLGetData(hStmt, 3, SQL_C_CHAR, address, sizeof(address), NULL);
            SQLGetData(hStmt, 4, SQL_C_CHAR, region, sizeof(region), NULL);
            SQLGetData(hStmt, 5, SQL_C_SLONG, &submissionTime, sizeof(submissionTime), NULL);
            SQLGetData(hStmt, 6, SQL_C_CHAR, status, sizeof(status), NULL);

            Applicant* app = new Applicant();
            app->id = id;
            app->name = name;
            app->address = address;
            app->region = region;
            app->submissionTime = submissionTime;
            app->status = status;

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
        SQLFreeHandle(SQL_HANDLE_STMT, hStmt);
    }

public:
    KtpSystem() : head(nullptr), tail(nullptr), revisionStackTop(nullptr) {
        connectToDB();
        loadFromDB();
    }

    ~KtpSystem() {
        disconnectFromDB();
        // Cleanup memory for linked list
        Applicant* current = head;
        while (current) {
            Applicant* next = current->next;
            delete current;
            current = next;
        }
        // Cleanup revision stack
        while (revisionStackTop) {
            Applicant* temp = revisionStackTop;
            revisionStackTop = revisionStackTop->next;
            delete temp;
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

        // Add to main linked list
        if (!head) {
            head = tail = newApp;
        } else {
            tail->next = newApp;
            newApp->prev = tail;
            tail = newApp;
        }
        idMap[newApp->id] = newApp;

        // Insert into Azure SQL Database
        string insertQuery = "INSERT INTO Applicants (id, name, address, region, submissionTime, status) VALUES ('" +
                             newApp->id + "', '" + newApp->name + "', '" + newApp->address + "', '" + newApp->region +
                             "', " + to_string(newApp->submissionTime) + ", '" + newApp->status + "')";
        if(!executeSQL(insertQuery))
            cout << "Error inserting application into DB.\n";
    }

    void processVerification() {
        if (!head) return;
        Applicant* toProcess = head;
        head = head->next;
        if (head) head->prev = nullptr;
        else tail = nullptr;

        // Mark as verified and remove from in-memory structure
        toProcess->status = "verified";
        idMap.erase(toProcess->id);

        // Remove from Azure SQL Database
        string deleteQuery = "DELETE FROM Applicants WHERE id = '" + toProcess->id + "'";
        if(!executeSQL(deleteQuery))
            cout << "Error deleting application from DB.\n";

        delete toProcess;
    }

    void editApplication(const string& id, const string& newName, 
                         const string& newAddress, const string& newRegion) {
        if (idMap.find(id) == idMap.end()) return;
        Applicant* app = idMap[id];
        
        // Push current state to revision stack
        Applicant* revision = new Applicant(*app);
        revision->next = revisionStackTop;
        revisionStackTop = revision;
        
        // Update in-memory record
        app->name = newName;
        app->address = newAddress;
        app->region = newRegion;
        app->status = "revision";
        
        // Update record in Azure SQL Database
        string updateQuery = "UPDATE Applicants SET name = '" + newName + "', address = '" + newAddress +
                             "', region = '" + newRegion + "', status = 'revision' WHERE id = '" + id + "'";
        if(!executeSQL(updateQuery))
            cout << "Error updating application in DB.\n";
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
        
        // Update record in Azure SQL Database
        string updateQuery = "UPDATE Applicants SET name = '" + current->name + "', address = '" + current->address +
                             "', region = '" + current->region + "', status = 'pending' WHERE id = '" + id + "'";
        if(!executeSQL(updateQuery))
            cout << "Error restoring application in DB.\n";
        
        delete revision;
    }

    // Note: Sorting the in-memory linked list will not change the order of records in the DB.
    void sortByRegion() {
        bool swapped;
        do {
            swapped = false;
            Applicant** ptr = &head;
            while ((*ptr) && (*ptr)->next) {
                Applicant* a = *ptr;
                Applicant* b = a->next;
                if (a->region > b->region) {
                    // Swap nodes in the linked list
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
        bool swapped;
        do {
            swapped = false;
            Applicant** ptr = &head;
            while ((*ptr) && (*ptr)->next) {
                Applicant* a = *ptr;
                Applicant* b = a->next;
                if (a->submissionTime > b->submissionTime) {
                    // Swap nodes in the linked list
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
};

int main() {
    KtpSystem system;
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
