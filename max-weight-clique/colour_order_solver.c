#define _GNU_SOURCE
#define _POSIX_SOURCE

#include "c_program_timing.h"
#include "graph.h"
#include "sorting.h"
#include "bitset.h"
#include "vertex_ordering.h"
#include "util.h"
#include "colour_order_solver.h"

#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

void colouring_bound_for_independent_set(struct Graph *g, int i, bool *in_P, long *residual_wt, long *bound, long *cumulative_wt_bound,
                                         struct UnweightedVtxList *P, int *times_to_visit) {
    long class_min_wt = LONG_MAX;
    int initial_P_size = P->size + 1;
    for (int j = 0; j < independent_set_size(g, i); j++)
        if (in_P[g->independent_sets[i][j]] && residual_wt[g->independent_sets[i][j]] < class_min_wt)
            class_min_wt = residual_wt[g->independent_sets[i][j]];
    *bound += class_min_wt;
    
    for (int j = 0; j < independent_set_size(g, i); j++) {
        residual_wt[g->independent_sets[i][j]] -= class_min_wt;
        if (--times_to_visit[g->independent_sets[i][j]] == 0) {
            times_to_visit[g->independent_sets[i][j]] = -1;
            cumulative_wt_bound[P->size] = *bound + residual_wt[g->independent_sets[i][j]];
            P->vv[P->size++] = g->independent_sets[i][j];
        }
    }

    //printf("%d - %d = %d\n", P->size, initial_P_size, P->size - initial_P_size);
    if (P->size - initial_P_size > 1) {
        INSERTION_SORT(int, (P->vv + initial_P_size), P->size - initial_P_size,
                       cumulative_wt_bound[initial_P_size + j - 1] < cumulative_wt_bound[initial_P_size + j]);
        INSERTION_SORT(int, (cumulative_wt_bound + initial_P_size), P->size - initial_P_size,
                       cumulative_wt_bound[initial_P_size + j - 1] < cumulative_wt_bound[initial_P_size + j]);
    }
}

// For each vertex in P, calculate a lower bound on clique weight if we choose to include that vertex.
// Sets up P and cumulative_wt_bound to contain all vertices that can be included in the clique.
// Returns how many vertices of the smallest independent set are in P. 0 means the independent set is impossible to satisfy.
// -1 means all the constraints are satisfied.
int colouring_bound(struct Graph *g, struct UnweightedVtxList *P, struct VtxList *C,
        long *cumulative_wt_bound)
{
    long bound = 0;
    long *residual_wt = calloc(g->n, sizeof *residual_wt);
    bool *in_P = calloc(g->n, sizeof *in_P);
    bool *in_C = calloc(g->n, sizeof *in_C);
    int *times_to_visit = calloc(g->n, sizeof *times_to_visit);
    int smallest_independent_set = 0, min_vertices_in_P = INT_MAX;
    bool *independent_set_satisfied = calloc(g->v1 + g->v2 + g->e1 + g->e2, sizeof *independent_set_satisfied);

    for (int i = 0; i < P->size; i++) {
        residual_wt[P->vv[i]] = g->weight[P->vv[i]];
        in_P[P->vv[i]] = true;
        times_to_visit[P->vv[i]] = (insertion_or_deletion(g, P->vv[i])) ? 1 : 2;
    }
    for (int i = 0; i < C->size; i++)
        in_C[C->vv[i]] = true;

    // choose the smallest independent set to explore first (i.e., put it at the end of P)
    for (int i = 0; i < g->v1 + g->v2 + g->e1 + g->e2; i++) {
        int how_many_vertices_in_P = 0;
        for (int j = 0; j < independent_set_size(g, i); j++) {
            if (in_C[g->independent_sets[i][j]]) {
                independent_set_satisfied[i] = true;
                break;
            }
            if (in_P[g->independent_sets[i][j]])
                how_many_vertices_in_P++;
        }
        if (!independent_set_satisfied[i]) {
            if (how_many_vertices_in_P == 0) {
                // the independent set is impossible to satisfy
                free(residual_wt);
                free(in_P);
                free(in_C);
                free(times_to_visit);
                free(independent_set_satisfied);
                return 0;
            }
            if (how_many_vertices_in_P < min_vertices_in_P) {
                smallest_independent_set = i;
                min_vertices_in_P = how_many_vertices_in_P;
            }
        }
    }

    if (min_vertices_in_P == INT_MAX) {
        // all the constraints are satisfied
        free(residual_wt);
        free(in_P);
        free(in_C);
        free(times_to_visit);
        free(independent_set_satisfied);
        return -1;
    }
    P->size = 0;

    for (int i = 0; i < g->v1 + g->v2 + g->e1 + g->e2; i++) // for each independent set
        if (!independent_set_satisfied[i] && i != smallest_independent_set)
            colouring_bound_for_independent_set(g, i, in_P, residual_wt, &bound, cumulative_wt_bound, P, times_to_visit);
    colouring_bound_for_independent_set(g, smallest_independent_set, in_P, residual_wt, &bound, cumulative_wt_bound, P, times_to_visit);

    free(residual_wt);
    free(in_P);
    free(in_C);
    free(times_to_visit);
    free(independent_set_satisfied);
    return min_vertices_in_P;
}

void expand(struct Graph *g, struct VtxList *C, struct UnweightedVtxList *P,
        struct VtxList *incumbent, int level, long *expand_call_count,
        bool quiet)
{
    (*expand_call_count)++;
    if (*expand_call_count % 100000 == 0)
        check_for_timeout();
    if (is_timeout_flag_set()) return;

    long *cumulative_wt_bound = malloc(g->n * sizeof *cumulative_wt_bound);
    int ind_set_size = colouring_bound(g, P, C, cumulative_wt_bound);
    if (ind_set_size == 0) {
        free(cumulative_wt_bound);
        return;
    }

    if (ind_set_size == -1) { // all constraints are satisfied
        if (incumbent->size == 0 || C->total_wt < incumbent->total_wt) { // we found a better solution
            copy_VtxList(C, incumbent);
            if (!quiet) {
                long elapsed_msec = get_elapsed_time_msec();
                printf("New incumbent: weight %ld at time %ld ms after %ld expand calls\n",
                       incumbent->total_wt, elapsed_msec, *expand_call_count);
            }
        }
        free(cumulative_wt_bound);
        return; // adding more is not going to make it better
    }

    printf("P:");
    for (int i = 0; i < P->size; i++)
        printf(" %d", P->vv[i]);
    printf("\n%d\n", ind_set_size);

    struct UnweightedVtxList new_P;
    init_UnweightedVtxList(&new_P, g->n);

    for (int i = P->size - 1; i >= P->size - ind_set_size && (incumbent->size == 0 || C->total_wt + cumulative_wt_bound[i] < incumbent->total_wt); i--) {
        int v = P->vv[i];

        new_P.size = 0;
        for (int j=0; j<i; j++) {
            int w = P->vv[j];
            if (g->adjmat[v][w])
                new_P.vv[new_P.size++] = w;
        }

        vtxlist_push_vtx(g, C, v);
        expand(g, C, &new_P, incumbent, level+1, expand_call_count, quiet);
        vtxlist_pop_vtx(g, C);
    }

    destroy_UnweightedVtxList(&new_P);
    free(cumulative_wt_bound);
}

void mc(struct Graph* g, long *expand_call_count, bool quiet, int vtx_ordering, struct VtxList *incumbent)
{
    calculate_all_degrees(g);

    int *vv = malloc(g->n * sizeof *vv);
    order_vertices(vv, g, vtx_ordering);

    struct Graph *ordered_graph = induced_subgraph(g, vv, g->n);
    populate_bit_complement_nd(ordered_graph);

    struct UnweightedVtxList P;
    init_UnweightedVtxList(&P, ordered_graph->n);
    for (int v=0; v<g->n; v++) P.vv[P.size++] = v;
    struct VtxList C;
    init_VtxList(&C, ordered_graph->n);
    expand(ordered_graph, &C, &P, incumbent, 0, expand_call_count, quiet);
    destroy_VtxList(&C);
    destroy_UnweightedVtxList(&P);

    // Use vertex indices from original graph
    for (int i=0; i<incumbent->size; i++)
        incumbent->vv[i] = vv[incumbent->vv[i]];

    free_graph(ordered_graph);
    free(vv);
}
