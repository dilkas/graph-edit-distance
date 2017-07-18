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

// For each vertex in P, calculate a lower bound on clique weight if we choose to include that vertex.
// Sets up P and cumulative_wt_bound to contain all vertices that can be included in the clique.
// Returns false if some constraint cannot be satisfied, true otherwise.
bool colouring_bound(struct Graph *g, struct UnweightedVtxList *P, struct VtxList *C,
        long *cumulative_wt_bound, bool tavares_style)
{
    long bound = 0;
    long *residual_wt = calloc(g->n, sizeof *residual_wt);
    bool *in_P = calloc(g->n, sizeof *in_P);
    bool *in_C = calloc(g->n, sizeof *in_C);
    int *times_to_visit = calloc(g->n, sizeof *times_to_visit);

    for (int i=0; i<P->size; i++) {
        residual_wt[P->vv[i]] = g->weight[P->vv[i]];
        in_P[P->vv[i]] = true;
        times_to_visit[P->vv[i]] = (insertion_or_deletion(g, P->vv[i])) ? 1 : 2;
    }
    for (int i=0; i<C->size; i++)
        in_C[C->vv[i]] = true;

    P->size = 0;

    for (int i=0; i < g->v1 + g->v2 + g->e1 + g->e2; i++) { // for each independent set
        int initial_P_size = P->size;
        long class_min_wt = LONG_MAX;
        bool constraint_is_satisfied = false;
        for (int j=0; j<independent_set_size(g, i); j++) {
            if (in_P[g->independent_sets[i][j]] && residual_wt[g->independent_sets[i][j]] < class_min_wt)
                class_min_wt = residual_wt[g->independent_sets[i][j]];
            if (in_C[g->independent_sets[i][j]]) {
                // checked: this is faster than keeping an array indicating which constraints are satisfied
                class_min_wt = LONG_MAX;
                constraint_is_satisfied = true;
                break; // if we already satisfy a set, there's no need to pick more vertices from it
            }
        }
        if (class_min_wt == LONG_MAX) {
            if (!constraint_is_satisfied) {
                // all the vertices are not in P
                free(residual_wt);
                free(in_P);
                free(in_C);
                free(times_to_visit);
                return false;
            }
            continue;
        }
        bound += class_min_wt;

        for (int j=0; j<independent_set_size(g, i); j++) {
            residual_wt[g->independent_sets[i][j]] -= class_min_wt;
            if (--times_to_visit[g->independent_sets[i][j]] == 0) {
                times_to_visit[g->independent_sets[i][j]] = -1;
                cumulative_wt_bound[P->size] = bound + residual_wt[g->independent_sets[i][j]];
                P->vv[P->size++] = g->independent_sets[i][j];
            }
        }
        INSERTION_SORT(int, (P->vv+initial_P_size), P->size - initial_P_size,
                       cumulative_wt_bound[initial_P_size + j - 1] < cumulative_wt_bound[initial_P_size + j]);
        INSERTION_SORT(int, (cumulative_wt_bound+initial_P_size), P->size - initial_P_size,
                       cumulative_wt_bound[initial_P_size + j - 1] < cumulative_wt_bound[initial_P_size + j]);
    }
    free(residual_wt);
    free(in_P);
    free(in_C);
    free(times_to_visit);
    return true;
}

void expand(struct Graph *g, struct VtxList *C, struct UnweightedVtxList *P,
        struct VtxList *incumbent, int level, long *expand_call_count,
        bool quiet, bool tavares_colour)
{
    (*expand_call_count)++;
    if (*expand_call_count % 100000 == 0)
        check_for_timeout();
    if (is_timeout_flag_set()) return;

    long *cumulative_wt_bound = malloc(g->n * sizeof *cumulative_wt_bound);
    if (!colouring_bound(g, P, C, cumulative_wt_bound, tavares_colour)) {
        free(cumulative_wt_bound);
        return;
    }

    if (P->size == 0 && (incumbent->size == 0 || C->total_wt < incumbent->total_wt)) {
        copy_VtxList(C, incumbent);
        if (!quiet) {
            long elapsed_msec = get_elapsed_time_msec();
            printf("New incumbent: weight %ld at time %ld ms after %ld expand calls\n",
                   incumbent->total_wt, elapsed_msec, *expand_call_count);
        }
    }

    struct UnweightedVtxList new_P;
    init_UnweightedVtxList(&new_P, g->n);

    for (int i = P->size-1; i >= 0 && (incumbent->size == 0 || C->total_wt + cumulative_wt_bound[i] < incumbent->total_wt); i--) {
        int v = P->vv[i];

        new_P.size = 0;
        for (int j=0; j<i; j++) {
            int w = P->vv[j];
            if (g->adjmat[v][w]) {
                new_P.vv[new_P.size++] = w;
            }
        }

        vtxlist_push_vtx(g, C, v);
        expand(g, C, &new_P, incumbent, level+1, expand_call_count, quiet, tavares_colour);
        vtxlist_pop_vtx(g, C);
    }

    destroy_UnweightedVtxList(&new_P);
    free(cumulative_wt_bound);
}

void mc(struct Graph* g, long *expand_call_count,
        bool quiet, bool tavares_colour, int vtx_ordering, struct VtxList *incumbent)
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
    expand(ordered_graph, &C, &P, incumbent, 0, expand_call_count, quiet, tavares_colour);
    destroy_VtxList(&C);
    destroy_UnweightedVtxList(&P);

    // Use vertex indices from original graph
    for (int i=0; i<incumbent->size; i++)
        incumbent->vv[i] = vv[incumbent->vv[i]];

    free_graph(ordered_graph);
    free(vv);
}
