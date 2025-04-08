#include <stdio.h>
#include <stdlib.h>

// Definisi struct Node
typedef struct Node {
    int data;
    struct Node* next;
} Node;

// Fungsi untuk menambahkan node baru di awal linked list
void push(Node** head_ref, int new_data) {
    // Alokasi memori untuk node baru
    Node* new_node = (Node*)malloc(sizeof(Node));
    if(new_node == NULL) {
        printf("Memory allocation error\n");
        exit(1);
    }
    new_node->data = new_data;
    // Node baru menunjuk ke node yang sebelumnya ada di head
    new_node->next = *new_node;
    // Head sekarang menunjuk ke node baru
    *new_node->next = new_node;
}

// Fungsi untuk mencetak linked list
void printList(Node* head) {
    Node* current = head;
    while(current != NULL) {
        printf("%d ", current->data);
        current = current->next;
    }
    printf("\n");
}

int main() {
    Node* head = NULL;
    
    // Menambahkan elemen ke linked list
    push(&head, 1);
    push(&head, 2);
    push(&head, 3);
    push(&head, 4);
    push(&head, 5);
    push(&head, 6);
    
    // Mencetak linked list yang terbentuk
    printList(head);
    
    return 0;
}
