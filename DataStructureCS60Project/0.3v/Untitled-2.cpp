#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <pqxx/pqxx>
#include <ctime>
#include <stdexcept>
using namespace std;
using namespace pqxx;

// Convert Unix timestamp to PostgreSQL-compatible timestamp string
string timeToStr(time_t t) {
    tm* tm = localtime(&t);
    char buf[20];
    strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", tm);
    return string(buf);
}

int main() {
    try {
        // Read file
        ifstream file("ktp_data.txt");
        if (!file) throw runtime_error("Failed to open file");

        vector<string> lines;
        string line;
        while (getline(file, line)) {
            lines.push_back(line);
        }

        // Validate line count
        if (lines.size() % 6 != 0) {
            throw runtime_error("Invalid file format: Line count not divisible by 6");
        }

        // Connect to PostgreSQL
        connection conn("user=postgres password=797985 host=localhost dbname=id-application port=5432");
        work txn(conn);

        // Process entries in batches of 6 lines
        for (size_t i = 0; i < lines.size(); i += 6) {
            string id = lines[i];
            string name = lines[i+1];
            string address = lines[i+2];
            string region = lines[i+3];
            
            // Convert submission time
            time_t submissionTime;
            try {
                submissionTime = stol(lines[i+4]);
            } catch (...) {
                throw runtime_error("Invalid timestamp at line " + to_string(i+5));
            }
            
            string status = lines[i+5];

            // Execute INSERT query
            txn.exec_params(
                "INSERT INTO applicants (id, name, address, region, submission_time, status) "
                "VALUES ($1, $2, $3, $4, $5, $6)",
                id, name, address, region, timeToStr(submissionTime), status
            );
        }

        txn.commit();
        cout << "Successfully uploaded " << lines.size()/6 << " records to PostgreSQL.\n";
    } catch (const exception &e) {
        cerr << "Error: " << e.what() << endl;
        return 1;
    }
    return 0;
}