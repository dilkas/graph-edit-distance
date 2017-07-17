#define _GNU_SOURCE

#include "graph.h"
#include "util.h"
#include "bitset.h"

#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void add_edge(struct Graph *g, int v, int w) {
    g->adjmat[v][w] = true;
    g->adjmat[w][v] = true;
}

void calculate_all_degrees(struct Graph *g) {
    for (int v=0; v<g->n; v++) {
        g->degree[v] = 0;
        for (int w=0; w<g->n; w++)
            g->degree[v] += g->adjmat[v][w];
    }
}

void populate_bit_complement_nd(struct Graph *g) {
    for (int i=0; i<g->n; i++) {
        for (int j=0; j<g->n; j++) {
            if (!g->adjmat[i][j] && i!=j)
                set_bit(g->bit_complement_nd[i], j);
        }
    }
}

// Checks if a set of vertices induces a clique
bool check_clique(struct Graph* g, struct VtxList* clq) {
    long total_wt = 0;
    for (int i=0; i<clq->size; i++)
        total_wt += g->weight[clq->vv[i]];
    if (total_wt == clq->total_wt)
        return true;

    for (int i=0; i<clq->size-1; i++)
        for (int j=i+1; j<clq->size; j++)
            if (!g->adjmat[clq->vv[i]][clq->vv[j]])
                return false;
    return true;
}

int independent_set_size(struct Graph *g, int index) {
    if (index < g->v1)
        return g->v2 + 1;
    if (index < g->v1 + g->v2)
        return g->v1 + 1;
    if (index < g->v1 + g->v2 + g->e1)
        return g->e2 + 1;
    return g->e1 + 1;
}

// Does is vertex represent an insertion or deletion operation?
bool insertion_or_deletion(struct Graph *g, int vertex) {
    if (vertex<g->v2)
        return true;
    if (vertex < (g->v1 + 1) * (g->v2 + 1) - 1) {
        if (vertex % (g->v2 + 1) == g->v2)
            return true;
        return false;
    }
    vertex -= (g->v1 + 1) * (g->v2 + 1) - 1;
    return vertex<g->e2 || vertex % (g->e2 + 1) == g->e2;
}

bool constraints_satisfied(struct Graph *g, struct VtxList *C) {
    for (int i=0; i < g->v1 + g->v2 + g->e1 + g->e2; i++) {
        for (int j=0; j<independent_set_size(g, i); j++) {
            for (int k=0; k < C->size; k++) {
                if (g->independent_sets[i][j] == C->vv[k])
                    goto check_next_constraint;
            }
        }
        return false;
    check_next_constraint: ;
    }
    return true;
}

struct Graph *new_graph(int n, int v1, int v2, int e1, int e2)
{
    struct Graph *g = calloc(1, sizeof(*g));
    g->n = n;
    g->v1 = v1;
    g->v2 = v2;
    g->e1 = e1;
    g->e2 = e2;
    g->degree = calloc(n, sizeof(*g->degree));
    g->weight = calloc(n, sizeof(*g->weight));
    g->weighted_deg = calloc(n, sizeof(*g->weighted_deg));
    g->adjmat = calloc(n, sizeof(*g->adjmat));
    g->bit_complement_nd = calloc(n, sizeof(*g->bit_complement_nd));
    for (int i=0; i<n; i++) {
        g->adjmat[i] = calloc(n, sizeof *g->adjmat[i]);
        g->bit_complement_nd[i] = calloc((n+BITS_PER_WORD-1)/BITS_PER_WORD, sizeof *g->bit_complement_nd[i]);
    }
    g->independent_sets = calloc(v1 + v2 + e1 + e2, sizeof(*g->independent_sets));
    for (int i=0; i<v1+v2+e1+e2; i++)
        g->independent_sets[i] = calloc(independent_set_size(g, i), sizeof(**g->independent_sets));
    return g;
}

void free_graph(struct Graph *g)
{
    for (int i=0; i<g->n; i++) {
        free(g->adjmat[i]);
        free(g->bit_complement_nd[i]);
    }
    for (int i=0; i < g->v1 + g->v2 + g->e1 + g->e2; i++)
        free(g->independent_sets[i]);
    free(g->independent_sets);
    free(g->degree);
    free(g->weighted_deg);
    free(g->weight);
    free(g->adjmat);
    free(g->bit_complement_nd);
    free(g);
}

struct Graph *induced_subgraph(struct Graph *g, int *vv, int vv_len) {
    struct Graph* subg = new_graph(vv_len, g->v1, g->v2, g->e1, g->e2);
    for (int i=0; i<subg->n; i++)
        for (int j=0; j<subg->n; j++)
            subg->adjmat[i][j] = g->adjmat[vv[i]][vv[j]];

    for (int i=0; i<subg->n; i++)
        subg->weight[i] = g->weight[vv[i]];

    for (int i=0; i < g->v1 + g->v2 + g->e1 + g->e2; i++) {
        for (int j=0; j<independent_set_size(g, i); j++) {
            for (int k=0; k<g->n; k++) {
                if (g->independent_sets[i][j] == vv[k]) {
                    subg->independent_sets[i][j] = k;
                    break;
                }
            }
        }
    }
    return subg;
}

struct Graph *readGraph(char* filename) {
    FILE* f;
    
    if ((f=fopen(filename, "r"))==NULL)
        fail("Cannot open file");

    char* line = NULL;
    char* token;
    size_t nchar = 0;

    int nvertices = 0;
    int medges = 0;
    int v1, v2, e1, e2; // Vertices and edges in the original graphs, used to determine sizes of independent sets
    int j = 0; // Used to track which independent set is about to be read from file
    int v, w;
    int edges_read = 0;
    long wt;

    struct Graph *g = NULL;

    while (getline(&line, &nchar, f) != -1) {
        if (nchar > 0) {
            switch (line[0]) {
            case 'p':
                if (sscanf(line, "p edge %d %d %d %d %d %d", &nvertices, &medges, &v1, &v2, &e1, &e2)!=6)
                    fail("Error reading a line beginning with p.\n");
                printf("%d vertices\n", nvertices);
                printf("%d edges\n", medges);
                printf("%d vertices and %d edges in source graph\n", v1, e1);
                printf("%d vertices and %d edges in target graph\n", v2, e2);
                g = new_graph(nvertices, v1, v2, e1, e2);
                for (int i=0; i<nvertices; i++)
                    g->weight[i] = 1l;   // default weight
                break;
            case 'e':
                if (sscanf(line, "e %d %d", &v, &w)!=2)
                    fail("Error reading a line beginning with e.\n");
                add_edge(g, v-1, w-1);
                edges_read++;
                break;
            case 'n':
                if (sscanf(line, "n %d %ld", &v, &wt)!=2)
                    fail("Error reading a line beginning with n.\n");
                g->weight[v-1] = wt;
                break;
            case 's':
                token = strtok(line, " ");
                for (int i=0; (token = strtok(NULL, " ")) != NULL; i++)
                    g->independent_sets[j][i] = atoi(token)-1;
                j++;
                break;
            }
        }
    }

    if (medges>0 && edges_read != medges) fail("Unexpected number of edges.");

    fclose(f);
    return g;
}

void init_VtxList(struct VtxList *l, int capacity)
{
    l->vv = malloc(capacity * sizeof *l->vv);
    l->size = 0;
    l->total_wt = 0;
}

void destroy_VtxList(struct VtxList *l)
{
    free(l->vv);
}

void init_UnweightedVtxList(struct UnweightedVtxList *l, int capacity)
{
    l->vv = malloc(capacity * sizeof *l->vv);
    l->size = 0;
}

void destroy_UnweightedVtxList(struct UnweightedVtxList *l)
{
    free(l->vv);
}

void vtxlist_push_vtx(struct Graph *g, struct VtxList *L, int v)
{
    L->vv[L->size++] = v;
    L->total_wt += g->weight[v];
}

void vtxlist_pop_vtx(struct Graph *g, struct VtxList *L)
{
    L->size--;
    L->total_wt -= g->weight[L->vv[L->size]];
}

void copy_VtxList(struct VtxList *src, struct VtxList *dest)
{
    dest->size = src->size;
    dest->total_wt = src->total_wt;
    for (int i=0; i<src->size; i++)
        dest->vv[i] = src->vv[i];
}
