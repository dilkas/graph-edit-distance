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
#include <float.h>
#include <limits.h>
#include <string.h>

#define NUM_WORDS (g->n + BITS_PER_WORD - 1) / BITS_PER_WORD 
#define IMPOSSIBLE_TO_SATISFY -1
#define ALL_CONSTRAINTS_SATISFIED -2

void colouring_bound_for_independent_set(struct Graph *g, int i, double *residual_wt, double *bound, unsigned long long *P) {
    double class_min_wt = DBL_MAX;
    for (int j = 0; j < independent_set_size(g, i); j++)
        if (check_bit(P, g->independent_sets[i][j]) && residual_wt[g->independent_sets[i][j]] < class_min_wt)
            class_min_wt = residual_wt[g->independent_sets[i][j]];
    *bound += class_min_wt;
    
    for (int j = 0; j < independent_set_size(g, i); j++) {
        residual_wt[g->independent_sets[i][j]] -= class_min_wt;
        g->cumulative_wt_bound[i][j] = *bound + residual_wt[g->independent_sets[i][j]];
    }
}

// O(n + (v1+v2+e1+e2) * colouring_bound_for_independent_set)
int colouring_bound(struct Graph *g, unsigned long long *P, struct VtxList *C) {
    double bound = 0;
    double *residual_wt = malloc(g->n * sizeof *residual_wt);
    bool *in_C = calloc(g->n, sizeof *in_C);
    int smallest_independent_set = 0, min_vertices_in_P = INT_MAX;
    bool *independent_set_satisfied = calloc(g->v1 + g->v2 + g->e1 + g->e2, sizeof *independent_set_satisfied);

    for (int i = 0; i < g->n; i++)
        residual_wt[i] = g->weight[i];
    for (int i = 0; i < C->size; i++)
        in_C[C->vv[i]] = true;

    // choose the smallest independent set to explore first
    for (int i = 0; i < g->v1 + g->v2 + g->e1 + g->e2; i++) {
        int how_many_vertices_in_P = 0;
        for (int j = 0; j < independent_set_size(g, i); j++) {
            if (in_C[g->independent_sets[i][j]]) {
                independent_set_satisfied[i] = true;
                break;
            }
            if (check_bit(P, g->independent_sets[i][j]))
                how_many_vertices_in_P++;
        }
        if (!independent_set_satisfied[i]) {
            if (how_many_vertices_in_P == 0) {
                free(residual_wt);
                free(in_C);
                free(independent_set_satisfied);
                return IMPOSSIBLE_TO_SATISFY;
            }
            if (how_many_vertices_in_P < min_vertices_in_P) {
                smallest_independent_set = i;
                min_vertices_in_P = how_many_vertices_in_P;
            }
        }
    }

    if (min_vertices_in_P == INT_MAX) {
        free(residual_wt);
        free(in_C);
        free(independent_set_satisfied);
        return ALL_CONSTRAINTS_SATISFIED;
    }

    for (int i = 0; i < g->v1 + g->v2 + g->e1 + g->e2; i++)
        if (!independent_set_satisfied[i] && i != smallest_independent_set)
            colouring_bound_for_independent_set(g, i, residual_wt, &bound, P);
    colouring_bound_for_independent_set(g, smallest_independent_set, residual_wt, &bound, P);

    free(residual_wt);
    free(in_C);
    free(independent_set_satisfied);
    return smallest_independent_set;
}

void expand(struct Graph *g, struct VtxList *C, unsigned long long *P,
        struct VtxList *incumbent, int level, long *expand_call_count,
        bool quiet)
{
    int ind_set;
    struct UnweightedVtxList to_visit;

    (*expand_call_count)++;
    if (*expand_call_count % 100000 == 0)
        check_for_timeout();
    if (is_timeout_flag_set()) return;

    if ((ind_set = colouring_bound(g, P, C)) == IMPOSSIBLE_TO_SATISFY)
        return;
    if (ind_set == ALL_CONSTRAINTS_SATISFIED) {
        if (incumbent->size == 0 || C->total_wt < incumbent->total_wt) {
            // we found a better solution
            copy_VtxList(C, incumbent);
            if (!quiet) {
                long elapsed_msec = get_elapsed_time_msec();
                printf("New incumbent: weight %lf at time %ld ms after %ld expand calls\n",
                       incumbent->total_wt, elapsed_msec, *expand_call_count);
            }
        }
        return;
    }

    init_UnweightedVtxList(&to_visit, independent_set_size(g, ind_set));
    for (int i = 0; i < independent_set_size(g, ind_set); i++)
        if (check_bit(P, g->independent_sets[ind_set][i]))
            to_visit.vv[to_visit.size++] = i;
    INSERTION_SORT(int, to_visit.vv, to_visit.size,
                   g->cumulative_wt_bound[ind_set][to_visit.vv[j - 1]] > g->cumulative_wt_bound[ind_set][to_visit.vv[j]]);
    /*printf("%d:", level);
    for (int i = 0; i < to_visit.size; i++)
        printf(" (%d, %lf)", to_visit.vv[i], g->cumulative_wt_bound[ind_set][to_visit.vv[i]]);
        printf("\n");*/

    unsigned long long *new_P = malloc(NUM_WORDS * sizeof *new_P);
    for (int i = 0; i < to_visit.size && (incumbent->size == 0 ||
                                          C->total_wt + g->cumulative_wt_bound[ind_set][to_visit.vv[i]] < incumbent->total_wt); i++) {
        copy_bitset(P, new_P, NUM_WORDS);
        bitset_intersect_with(new_P, g->bit_complement_nd[g->independent_sets[ind_set][to_visit.vv[i]]], NUM_WORDS);
        vtxlist_push_vtx(g, C, g->independent_sets[ind_set][to_visit.vv[i]]);
        expand(g, C, new_P, incumbent, level + 1, expand_call_count, quiet);
        vtxlist_pop_vtx(g, C);
    }
    free(new_P);
}

void mc(struct Graph* g, long *expand_call_count, bool quiet, struct VtxList *incumbent)
{
    calculate_all_degrees(g);
    populate_bit_complement_nd(g);

    unsigned long long *P = malloc(NUM_WORDS * sizeof *P);
    for (int i = 0; i < NUM_WORDS; i++)
        P[i] |= ~0;

    struct VtxList C;
    init_VtxList(&C, g->n);

    expand(g, &C, P, incumbent, 0, expand_call_count, quiet);

    destroy_VtxList(&C);
    free(P);
}
