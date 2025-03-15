#include <iostream>
#include <bits/stdc++.h>
using namespace std;

struct ListNode {
    int val;
    ListNode* next;
    ListNode(int x) : val(x), next(nullptr) {}
};

class Solution {
    public:
        ListNode* reverseKGroup(ListNode* head, int k) {
            if (head == nullptr || k == 1) return head;

            ListNode dummy(0);
            dummy.next = head;
            ListNode* prevTail = &dummy;

            while (true) {
                ListNode* groupStart = prevTail->next;
                ListNode* check = groupStart;
                int count = 0;

                // Check if there are at least k nodes remaining
                while (count < k && check != nullptr) {
                    check = check->next;
                    count++;
                }
                if (count < k) break; // Not enough nodes to reverse

                // Reverse the k nodes
                ListNode* prev = nullptr;
                ListNode* current = groupStart;
                for (int i = 0; i < k; ++i) {
                    ListNode* nextNode = current->next;
                    current->next = prev;
                    prev = current;
                    current = nextNode;
                }

                // Reconnect the reversed group to the previous part
                prevTail->next = prev;
                groupStart->next = current;
                prevTail = groupStart;
            }

            return dummy.next;
        }
};

int main() {
    Solution solution;
    ListNode* head = new ListNode(1);
    head->next = new ListNode(2);
    head->next->next = new ListNode(3);
    head->next->next->next = new ListNode(4);
    head->next->next->next->next = new ListNode(5);

    ListNode* result = solution.reverseKGroup(head, 2);

    while (result != nullptr) {
        cout << result->val << " ";
        result = result->next;
    }
    cout << endl;

    return 0;
}
