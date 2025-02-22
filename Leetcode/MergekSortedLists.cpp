#include <iostream>
#include <vector>
#include <queue>
using namespace std;

struct ListNode {
    int val;
    ListNode *next;
    ListNode() : val(0), next(nullptr) {}
    ListNode(int x) : val(x), next(nullptr) {}
    ListNode(int x, ListNode *next) : val(x), next(next) {}
};

class Solution {
public:
    ListNode* mergeKLists(vector<ListNode*>& lists) {
        // Comparator for the priority queue to create a min-heap
        auto comp = [](ListNode* a, ListNode* b) { return a->val > b->val; };
        priority_queue<ListNode*, vector<ListNode*>, decltype(comp)> min_heap(comp);
        
        // Push the head of each non-empty list into the heap
        for (ListNode* list : lists) {
            if (list != nullptr) {
                min_heap.push(list);
            }
        }
        
        // Dummy node to build the merged list
        ListNode dummy(0);
        ListNode* tail = &dummy;
        
        while (!min_heap.empty()) {
            // Extract the smallest node
            ListNode* node = min_heap.top();
            min_heap.pop();
            
            // Append to the merged list
            tail->next = node;
            tail = tail->next;
            
            // Push the next node of the extracted node into the heap
            if (node->next != nullptr) {
                min_heap.push(node->next);
            }
        }
        
        return dummy.next;
    }
};

int main() {
    Solution solution;
    vector<ListNode*> lists;
    ListNode* list1 = new ListNode(79);
    list1->next = new ListNode(4);
    list1->next->next = new ListNode(5);
    lists.push_back(list1);
    
    ListNode* list2 = new ListNode(1);
    list2->next = new ListNode(3);
    list2->next->next = new ListNode(4);
    lists.push_back(list2);
    
    ListNode* list3 = new ListNode(2);
    list3->next = new ListNode(6);
    lists.push_back(list3);
    
    ListNode* mergedList = solution.mergeKLists(lists);
    
    // Print the merged list
    while (mergedList != nullptr) {
        cout << mergedList->val << " ";
        mergedList = mergedList->next;
    }
    cout << endl;
}