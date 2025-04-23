#include <stdio.h>
#define MAXNUM_VERTICES 100
#define Inf 1000000000

typedef enum {WHITE, GRAY , BLACK} Color;

int finish_time[MAXNUM_VERTICES];
int time = 0;

typedef struct {
    int n_vertices;
    int n_edges;
    int adjacency_matrix[MAXNUM_VERTICES][MAXNUM_VERTICES];
} Graph;

int DFS_visit(Graph *g, Color *vertex_colors, int v) {
    int i;
    
    vertex_colors[v] = GRAY;
    
    for(i = 0; i < g->n_vertices; i++) {
        if(g->adjacency_matrix[v][i] == 1) {
            if(vertex_colors[i] == GRAY) {
                printf("1");
                return 1;
            }
            if(vertex_colors[i] == WHITE) {
                if(DFS_visit(g, vertex_colors, i)) {
                    return 1;
                }
            }
        }
    }
    vertex_colors[v] = BLACK;
    return 0;
}

void DFS_visit2(Graph *g, Color *vertex_colors, int v) {
    int i;
    
    printf("%d time = %d\n", v, time);

    vertex_colors[v] = GRAY;
    
    for(i = 0; i < g->n_vertices; i++) {
        if(g->adjacency_matrix[v][i] == 1 && vertex_colors[i] == WHITE) {
            DFS_visit2(g, vertex_colors, i);
        }
    }
    vertex_colors[v] = BLACK;
    finish_time[v] = ++time;
}

int DFS(Graph *g) {
    Color vertex_colors[MAXNUM_VERTICES];
    int i;
    
    for(i = 0; i < g->n_vertices; i++) {
        vertex_colors[i] = WHITE;
    }
    for(i = 0; i < g->n_vertices; i++) {
        if(vertex_colors[i] == WHITE) {
            if(DFS_visit(g, vertex_colors, i))
                return 1;
        }
    }
    printf("0");
    return 0;
}

void DFS2(Graph *g) {
    Color vertex_colors[MAXNUM_VERTICES];
    int i;
    
    for(i = 0; i < g->n_vertices; i++) {
        vertex_colors[i] = WHITE;
    }
    for(i = 0; i < g->n_vertices; i++) {
        finish_time[i] = Inf;
    }

    for(i = 0; i < g->n_vertices; i++) {
        if (vertex_colors[i] == WHITE){
            DFS_visit2(g, vertex_colors, i);
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

    DFS2(&g);
    for(i = 0; i < g.n_vertices; i++) {
        printf("%d ", finish_time[i]);
    }
    printf("\n");

    return 0;
}
