#include <iostream>
#include <string>
#include <unordered_map>
#include <queue>
#include <stack>
#include <vector>
#include <algorithm>
#include <sqlite3.h>

struct Applicant {
    std::string nik;
    std::string name;
    std::string address;
    std::string submission_time;
    std::string status;
};

class Database {
    sqlite3* db;
public:
    Database(const char* dbname) {
        if (sqlite3_open(dbname, &db) != SQLITE_OK) {
            std::cerr << "Can't open database: " << sqlite3_errmsg(db) << std::endl;
            exit(1);
        }
        createTables();
    }
    
    ~Database() {
        sqlite3_close(db);
    }
    
    void createTables() {
        const char* sql = 
            "CREATE TABLE IF NOT EXISTS applicants ("
            "nik TEXT PRIMARY KEY, "
            "name TEXT, "
            "address TEXT, "
            "submission_time DATETIME, "
            "status TEXT);"
            "CREATE TABLE IF NOT EXISTS verification_queue ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "nik TEXT, "
            "FOREIGN KEY(nik) REFERENCES applicants(nik));"
            "CREATE TABLE IF NOT EXISTS revisions ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "nik TEXT, "
            "FOREIGN KEY(nik) REFERENCES applicants(nik));";
        char* errMsg;
        if (sqlite3_exec(db, sql, nullptr, nullptr, &errMsg) != SQLITE_OK) {
            std::cerr << "SQL error: " << errMsg << std::endl;
            sqlite3_free(errMsg);
            exit(1);
        }
    }
    
    void addApplicant(const Applicant& applicant) {
        std::string sql = "INSERT INTO applicants VALUES (?, ?, ?, ?, ?);";
        sqlite3_stmt* stmt;
        if (sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr) != SQLITE_OK) {
            std::cerr << "Prepare failed: " << sqlite3_errmsg(db) << std::endl;
            return;
        }
        sqlite3_bind_text(stmt, 1, applicant.nik.c_str(), -1, SQLITE_TRANSIENT);
        sqlite3_bind_text(stmt, 2, applicant.name.c_str(), -1, SQLITE_TRANSIENT);
        sqlite3_bind_text(stmt, 3, applicant.address.c_str(), -1, SQLITE_TRANSIENT);
        sqlite3_bind_text(stmt, 4, applicant.submission_time.c_str(), -1, SQLITE_TRANSIENT);
        sqlite3_bind_text(stmt, 5, applicant.status.c_str(), -1, SQLITE_TRANSIENT);
        if (sqlite3_step(stmt) != SQLITE_DONE) {
            std::cerr << "Insert failed: " << sqlite3_errmsg(db) << std::endl;
        }
        sqlite3_finalize(stmt);
    }
    
    void enqueueVerification(const std::string& nik) {
        std::string sql = "INSERT INTO verification_queue (nik) VALUES (?);";
        sqlite3_stmt* stmt;
        if (sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr) != SQLITE_OK) {
            std::cerr << "Prepare enqueue failed: " << sqlite3_errmsg(db) << std::endl;
            return;
        }
        sqlite3_bind_text(stmt, 1, nik.c_str(), -1, SQLITE_TRANSIENT);
        if (sqlite3_step(stmt) != SQLITE_DONE) {
            std::cerr << "Enqueue failed: " << sqlite3_errmsg(db) << std::endl;
        }
        sqlite3_finalize(stmt);
    }
    
    std::string dequeueVerification() {
        std::string nik;
        sqlite3_stmt* stmt;
        std::string select_sql = "SELECT nik FROM verification_queue ORDER BY id ASC LIMIT 1;";
        if (sqlite3_prepare_v2(db, select_sql.c_str(), -1, &stmt, nullptr) != SQLITE_OK) {
            std::cerr << "Prepare dequeue select failed: " << sqlite3_errmsg(db) << std::endl;
            return "";
        }
        if (sqlite3_step(stmt) == SQLITE_ROW) {
            nik = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 0));
        }
        sqlite3_finalize(stmt);
        if (nik.empty()) {
            return "";
        }
        std::string delete_sql = "DELETE FROM verification_queue WHERE id = (SELECT id FROM verification_queue ORDER BY id ASC LIMIT 1);";
        if (sqlite3_prepare_v2(db, delete_sql.c_str(), -1, &stmt, nullptr) != SQLITE_OK) {
            std::cerr << "Prepare dequeue delete failed: " << sqlite3_errmsg(db) << std::endl;
            return "";
        }
        if (sqlite3_step(stmt) != SQLITE_DONE) {
            std::cerr << "Dequeue delete failed: " << sqlite3_errmsg(db) << std::endl;
        }
        sqlite3_finalize(stmt);
        return nik;
    }
    
    void pushRevision(const std::string& nik) {
        std::string sql = "INSERT INTO revisions (nik) VALUES (?);";
        sqlite3_stmt* stmt;
        if (sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr) != SQLITE_OK) {
            std::cerr << "Prepare push revision failed: " << sqlite3_errmsg(db) << std::endl;
            return;
        }
        sqlite3_bind_text(stmt, 1, nik.c_str(), -1, SQLITE_TRANSIENT);
        if (sqlite3_step(stmt) != SQLITE_DONE) {
            std::cerr << "Push revision failed: " << sqlite3_errmsg(db) << std::endl;
        }
        sqlite3_finalize(stmt);
    }
    
    std::string popRevision() {
        std::string nik;
        sqlite3_stmt* stmt;
        std::string select_sql = "SELECT nik FROM revisions ORDER BY id DESC LIMIT 1;";
        if (sqlite3_prepare_v2(db, select_sql.c_str(), -1, &stmt, nullptr) != SQLITE_OK) {
            std::cerr << "Prepare pop select failed: " << sqlite3_errmsg(db) << std::endl;
            return "";
        }
        if (sqlite3_step(stmt) == SQLITE_ROW) {
            nik = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 0));
        }
        sqlite3_finalize(stmt);
        if (nik.empty()) {
            return "";
        }
        std::string delete_sql = "DELETE FROM revisions WHERE id = (SELECT id FROM revisions ORDER BY id DESC LIMIT 1);";
        if (sqlite3_prepare_v2(db, delete_sql.c_str(), -1, &stmt, nullptr) != SQLITE_OK) {
            std::cerr << "Prepare pop delete failed: " << sqlite3_errmsg(db) << std::endl;
            return "";
        }
        if (sqlite3_step(stmt) != SQLITE_DONE) {
            std::cerr << "Pop delete failed: " << sqlite3_errmsg(db) << std::endl;
        }
        sqlite3_finalize(stmt);
        return nik;
    }
    
    void updateApplicantStatus(const std::string& nik, const std::string& status) {
        std::string sql = "UPDATE applicants SET status = ? WHERE nik = ?;";
        sqlite3_stmt* stmt;
        if (sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr) != SQLITE_OK) {
            std::cerr << "Prepare update status failed: " << sqlite3_errmsg(db) << std::endl;
            return;
        }
        sqlite3_bind_text(stmt, 1, status.c_str(), -1, SQLITE_TRANSIENT);
        sqlite3_bind_text(stmt, 2, nik.c_str(), -1, SQLITE_TRANSIENT);
        if (sqlite3_step(stmt) != SQLITE_DONE) {
            std::cerr << "Update status failed: " << sqlite3_errmsg(db) << std::endl;
        }
        sqlite3_finalize(stmt);
    }
    
    void loadApplicants(std::unordered_map<std::string, Applicant>& applicants) {
        std::string sql = "SELECT nik, name, address, submission_time, status FROM applicants;";
        sqlite3_stmt* stmt;
        if (sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr) != SQLITE_OK) {
            std::cerr << "Prepare load applicants failed: " << sqlite3_errmsg(db) << std::endl;
            return;
        }
        while (sqlite3_step(stmt) == SQLITE_ROW) {
            Applicant a;
            a.nik = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 0));
            a.name = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 1));
            a.address = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 2));
            a.submission_time = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 3));
            a.status = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 4));
            applicants[a.nik] = a;
        }
        sqlite3_finalize(stmt);
    }
    
    void loadVerificationQueue(std::queue<std::string>& queue) {
        std::string sql = "SELECT nik FROM verification_queue ORDER BY id ASC;";
        sqlite3_stmt* stmt;
        if (sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr) != SQLITE_OK) {
            std::cerr << "Prepare load queue failed: " << sqlite3_errmsg(db) << std::endl;
            return;
        }
        while (sqlite3_step(stmt) == SQLITE_ROW) {
            std::string nik = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 0));
            queue.push(nik);
        }
        sqlite3_finalize(stmt);
    }
    
    void loadRevisionsStack(std::stack<std::string>& stack) {
        std::string sql = "SELECT nik FROM revisions ORDER BY id DESC;";
        sqlite3_stmt* stmt;
        if (sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, nullptr) != SQLITE_OK) {
            std::cerr << "Prepare load stack failed: " << sqlite3_errmsg(db) << std::endl;
            return;
        }
        while (sqlite3_step(stmt) == SQLITE_ROW) {
            std::string nik = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 0));
            stack.push(nik);
        }
        sqlite3_finalize(stmt);
    }
};

class ApplicationManager {
private:
    Database db;
    std::unordered_map<std::string, Applicant> applicants;
    std::queue<std::string> verificationQueue;
    std::stack<std::string> revisionsStack;
    
public:
    ApplicationManager(const char* dbname) : db(dbname) {
        db.loadApplicants(applicants);
        db.loadVerificationQueue(verificationQueue);
        db.loadRevisionsStack(revisionsStack);
    }
    
    void submitApplication() {
        Applicant a;
        std::cout << "Enter NIK: ";
        std::getline(std::cin, a.nik);
        if (applicants.find(a.nik) != applicants.end()) {
            std::cout << "Applicant with this NIK already exists.\n";
            return;
        }
        std::cout << "Enter name: ";
        std::getline(std::cin, a.name);
        std::cout << "Enter address: ";
        std::getline(std::cin, a.address);
        std::cout << "Enter submission time (YYYY-MM-DD HH:MM:SS): ";
        std::getline(std::cin, a.submission_time);
        a.status = "pending";
        
        applicants[a.nik] = a;
        verificationQueue.push(a.nik);
        db.addApplicant(a);
        db.enqueueVerification(a.nik);
        std::cout << "Application submitted.\n";
    }
    
    void processVerification() {
        if (verificationQueue.empty()) {
            std::cout << "No applications to verify.\n";
            return;
        }
        std::string nik = verificationQueue.front();
        verificationQueue.pop();
        std::string currentNik = db.dequeueVerification();
        if (currentNik != nik) {
            std::cerr << "Error: Database and queue mismatch.\n";
            return;
        }
        Applicant& applicant = applicants[nik];
        
        std::cout << "Verifying applicant:\n"
                  << "NIK: " << applicant.nik << "\n"
                  << "Name: " << applicant.name << "\n"
                  << "Address: " << applicant.address << "\n"
                  << "Submit time: " << applicant.submission_time << "\n";
        std::cout << "Approve? (y/n): ";
        char choice;
        std::cin >> choice;
        std::cin.ignore();
        if (choice == 'y' || choice == 'Y') {
            applicant.status = "verified";
            db.updateApplicantStatus(nik, "verified");
            std::cout << "Applicant verified.\n";
        } else {
            applicant.status = "needs_revision";
            revisionsStack.push(nik);
            db.pushRevision(nik);
            db.updateApplicantStatus(nik, "needs_revision");
            std::cout << "Applicant marked for revision.\n";
        }
    }
    
    void processRevision() {
        if (revisionsStack.empty()) {
            std::cout << "No revisions to process.\n";
            return;
        }
        std::string nik = revisionsStack.top();
        revisionsStack.pop();
        std::string currentNik = db.popRevision();
        if (currentNik != nik) {
            std::cerr << "Error: Database and stack mismatch.\n";
            return;
        }
        Applicant& applicant = applicants[nik];
        std::cout << "Revising applicant data:\n"
                  << "NIK: " << applicant.nik << "\n"
                  << "Current name: " << applicant.name << "\n"
                  << "Current address: " << applicant.address << "\n";
        std::cout << "Enter new name (leave blank to keep current): ";
        std::string newName;
        std::getline(std::cin, newName);
        if (!newName.empty()) {
            applicant.name = newName;
        }
        std::cout << "Enter new address (leave blank to keep current): ";
        std::string newAddress;
        std::getline(std::cin, newAddress);
        if (!newAddress.empty()) {
            applicant.address = newAddress;
        }
        applicant.status = "pending";
        db.updateApplicantStatus(nik, "pending");
        verificationQueue.push(nik);
        db.enqueueVerification(nik);
        std::cout << "Applicant data revised and requeued for verification.\n";
    }
    
    void viewSortedByRegion() {
        std::vector<Applicant> sorted;
        for (auto& pair : applicants) {
            sorted.push_back(pair.second);
        }
        std::sort(sorted.begin(), sorted.end(), [](const Applicant& a, const Applicant& b) {
            return a.address < b.address;
        });
        std::cout << "Applicants sorted by region:\n";
        for (const auto& a : sorted) {
            std::cout << "NIK: " << a.nik << "\n"
                      << "Name: " << a.name << "\n"
                      << "Address: " << a.address << "\n"
                      << "Status: " << a.status << "\n"
                      << "----------------------------\n";
        }
    }
    
    void viewSortedByTime() {
        std::vector<Applicant> sorted;
        for (auto& pair : applicants) {
            sorted.push_back(pair.second);
        }
        std::sort(sorted.begin(), sorted.end(), [](const Applicant& a, const Applicant& b) {
            return a.submission_time < b.submission_time;
        });
        std::cout << "Applicants sorted by submission time:\n";
        for (const auto& a : sorted) {
            std::cout << "NIK: " << a.nik << "\n"
                      << "Name: " << a.name << "\n"
                      << "Address: " << a.address << "\n"
                      << "Submit time: " << a.submission_time << "\n"
                      << "Status: " << a.status << "\n"
                      << "----------------------------\n";
        }
    }
};

int main() {
    ApplicationManager manager("ktp.db");
    int choice;
    do {
        std::cout << "\nSistem Pengajuan KTP Online\n";
        std::cout << "1. Ajukan KTP\n";
        std::cout << "2. Proses Verifikasi\n";
        std::cout << "3. Proses Revisi\n";
        std::cout << "4. Lihat Pemohon berdasarkan Wilayah\n";
        std::cout << "5. Lihat Pemohon berdasarkan Waktu\n";
        std::cout << "6. Keluar\n";
        std::cout << "Pilihan: ";
        std::cin >> choice;
        std::cin.ignore();
        
        switch (choice) {
            case 1:
                manager.submitApplication();
                break;
            case 2:
                manager.processVerification();
                break;
            case 3:
                manager.processRevision();
                break;
            case 4:
                manager.viewSortedByRegion();
                break;
            case 5:
                manager.viewSortedByTime();
                break;
            case 6:
                std::cout << "Keluar.\n";
                break;
            default:
                std::cout << "Pilihan tidak valid.\n";
        }
    } while (choice != 6);
    return 0;
}