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

void colouring_bound(struct Graph *g, struct UnweightedVtxList *P, struct VtxList *C,
        long *cumulative_wt_bound, bool tavares_style)
{
    int max_v = 0;
    for (int i=0; i<P->size; i++)
        if (P->vv[i] > max_v)
            max_v = P->vv[i];
    long bound = 0;
    bool *not_written = calloc(g->n, sizeof *not_written);
    long *residual_wt = calloc(g->n, sizeof *residual_wt);
    bool *in_P = calloc(g->n, sizeof *in_P);
    bool *in_C = calloc(g->n, sizeof *in_C);
    int *times_to_visit = calloc(g->n, sizeof *times_to_visit);
    for (int i=0; i<P->size; i++) {
        residual_wt[P->vv[i]] = g->weight[P->vv[i]];
        not_written[P->vv[i]] = true;
        in_P[P->vv[i]] = true;
        times_to_visit[P->vv[i]] = (insertion_or_deletion(g, P->vv[i])) ? 1 : 2;
    }
    for (int i=0; i<C->size; i++)
        in_C[C->vv[i]] = true;

    P->size = 0;

    for (int i=0; i < g->v1 + g->v2 + g->e1 + g->e2; i++) {
        int initial_P_size = P->size;
        long class_max_wt = LONG_MIN;
        printf("class:");
        for (int j=0; j<independent_set_size(g, i); j++) {
            printf(" (%d, %d, %ld)", g->independent_sets[i][j], in_P[g->independent_sets[i][j]],
                   residual_wt[g->independent_sets[i][j]]);
            if (in_P[g->independent_sets[i][j]] && residual_wt[g->independent_sets[i][j]] > class_max_wt)
                class_max_wt = residual_wt[g->independent_sets[i][j]];
            if (in_C[g->independent_sets[i][j]]) {
                class_max_wt = 0;
                break;
            }
        }
        printf("\n");
        if (class_max_wt == LONG_MIN)
            continue;
        bound += class_max_wt;
        printf("class_max_wt: %ld\n", class_max_wt);
        printf("new bound: %ld\n", bound);

        for (int j=0; j<independent_set_size(g, i); j++) {
            residual_wt[g->independent_sets[i][j]] -= class_max_wt;
            times_to_visit[g->independent_sets[i][j]]--;
            // removed residual_wt[g->independent_sets[i][j]] == 0
            if (not_written[g->independent_sets[i][j]] && times_to_visit[g->independent_sets[i][j]] == 0) {
                not_written[g->independent_sets[i][j]] = false;
                cumulative_wt_bound[P->size] = bound + residual_wt[g->independent_sets[i][j]];
                P->vv[P->size++] = g->independent_sets[i][j];
                printf("added %d to P\n", P->vv[P->size-1]);
            }
        }
        INSERTION_SORT(int, (P->vv+initial_P_size), P->size - initial_P_size, cumulative_wt_bound[j-1] < cumulative_wt_bound[j]);
        INSERTION_SORT(int, (cumulative_wt_bound+initial_P_size), P->size - initial_P_size, cumulative_wt_bound[j-1] < cumulative_wt_bound[j]);
    }
    free(residual_wt);
    free(not_written);
    if (C->size == 0 && P->size != g->n)
        fail("Every vertex should be a plausible first choice");
}

void expand(struct Graph *g, struct VtxList *C, struct UnweightedVtxList *P,
        struct VtxList *incumbent, int level, long *expand_call_count,
        bool quiet, bool tavares_colour)
{
    (*expand_call_count)++;
    if (*expand_call_count % 100000 == 0)
        check_for_timeout();
    if (is_timeout_flag_set()) return;

    if (!quiet && (incumbent->size == 0 || C->total_wt>incumbent->total_wt) && constraints_satisfied(g, C)) {
        copy_VtxList(C, incumbent);
        long elapsed_msec = get_elapsed_time_msec();
        printf("New incumbent: weight %ld at time %ld ms after %ld expand calls\n",
                incumbent->total_wt, elapsed_msec, *expand_call_count);
    }

    long *cumulative_wt_bound = malloc(g->n * sizeof *cumulative_wt_bound);
    colouring_bound(g, P, C, cumulative_wt_bound, tavares_colour);

    printf("C:");
    for (int i=0; i<C->size; i++)
        printf(" %d", C->vv[i]);
    printf("\ncumulative weight bound:");
    for (int i=0; i<P->size; i++)
        printf("(%d %ld), ", P->vv[i], cumulative_wt_bound[i]);
    printf("\n\n");

    struct UnweightedVtxList new_P;
    init_UnweightedVtxList(&new_P, g->n);

    for (int i=P->size-1; i>=0 && (incumbent->size == 0 || C->total_wt+cumulative_wt_bound[i]>incumbent->total_wt); i--) {
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
