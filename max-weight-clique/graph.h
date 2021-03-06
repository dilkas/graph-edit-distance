#ifndef GRAPH_H
#define GRAPH_H

#include <limits.h>
#include <stdbool.h>

#define BYTES_PER_WORD sizeof(unsigned long long)
#define BITS_PER_WORD (CHAR_BIT * BYTES_PER_WORD)

struct Graph {
    int n, v1, v2, e1, e2;
    int *degree;
    long *weighted_deg;
    double *weight;
    bool **adjmat;
    unsigned long long **bit_complement_nd;
    int **independent_sets;
    double **cumulative_wt_bound;
};

struct VtxList {
    double total_wt;
    int size;
    int *vv;
};

struct UnweightedVtxList {
    int size;
    int *vv;
};

void init_VtxList(struct VtxList *l, int capacity);
void destroy_VtxList(struct VtxList *l);
void init_UnweightedVtxList(struct UnweightedVtxList *l, int capacity);
void destroy_UnweightedVtxList(struct UnweightedVtxList *l);

void add_edge(struct Graph *g, int v, int w);

void calculate_all_degrees(struct Graph *g);

// Checks if a set of vertices induces a clique
bool check_clique(struct Graph* g, struct VtxList* clq);

int independent_set_size(struct Graph *g, int index);

bool insertion_or_deletion(struct Graph *g, int vertex);

void populate_bit_complement_nd(struct Graph *g);

struct Graph *induced_subgraph(struct Graph *g, int *vv, int vv_len);

struct Graph *new_graph(int n, int v1, int v2, int e1, int e2);

void free_graph(struct Graph *g);

struct Graph *readGraph(char* filename);

void copy_VtxList(struct VtxList *src, struct VtxList *dest);

void vtxlist_push_vtx(struct Graph *g, struct VtxList *L, int v);

void vtxlist_pop_vtx(struct Graph *g, struct VtxList *L);

#endif
