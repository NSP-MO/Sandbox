#include <stdio.h>
#define MAXNUM_VERTICES 100

typedef enum {WHITE, GRAY , BLACK} Color;

typedef struct {
    int n_vertices;
    int n_edges;
    int adjacency_matrix[MAXNUM_VERTICES][MAXNUM_VERTICES];
} Graph;

void DFS_visit(Graph *g, Color *vertex_colors, int v) {
    
    int i;
    
    printf("%d ", v);
    vertex_colors[v] = GRAY;

    for(i = 0; i < g->n_vertices; i++) {
        if(g->adjacency_matrix[v][i] == 1 && vertex_colors[i] != WHITE) {
            printf("Cycle!\n");
        }
        if(g->adjacency_matrix[v][i] == 1 && vertex_colors[i] == WHITE) {
            DFS_visit(g, vertex_colors, i);
        }
    }
    vertex_colors[v] = BLACK;
}

void DFS(Graph *g) {

    Color vertex_colors[MAXNUM_VERTICES];
    int i;

    for(i = 0; i < g->n_vertices; i++) {
        vertex_colors[i] = WHITE;
    }
    for(i = 0; i < g->n_vertices; i++) {
        if(vertex_colors[i] == WHITE) {
            DFS_visit(g, vertex_colors, i);
        }
    }
    printf("\n");

}

int main() {

    Graph g;
    int n_vertices, n_edges, i, j;
    int a, b;

    scanf("%d %d", &n_vertices, &n_edges);
    g.n_vertices = n_vertices;
    g.n_edges = n_edges;

    for(i = 0; i < n_vertices; i++) {
        for(j = 0; j < n_vertices; j++) {
            g.adjacency_matrix[i][j] = 0;
        }
    }

    for(i = 0; i < MAXNUM_VERTICES; i++) {
        for(j = 0; j < MAXNUM_VERTICES; j++) {
            g.adjacency_matrix[i][j] = -1;
        }
    }

    for(i = 0; i < n_edges; i++) {
        scanf("%d %d", &a, &b);
        g.adjacency_matrix[a][b] = 1;
    }

    DFS(&g);
    printf("\n");

    return 0;
}
