#include <numeric>
#include <fwdpy11/types/DiploidPopulation.hpp>
#include <fwdpp/ts/count_mutations.hpp>
#include <fwdpp/internal/sample_diploid_helpers.hpp>
#include "index_and_count_mutations.hpp"

void
index_and_count_mutations(const bool suppress_edge_table_indexing,
                          fwdpy11::DiploidPopulation& pop)
{
    pop.mcounts_from_preserved_nodes.resize(pop.mutations.size(), 0);
    if (!suppress_edge_table_indexing)
        {
            return;
        }
    if (pop.tables.preserved_nodes.empty())
        {
            pop.tables.build_indexes();
            std::vector<std::int32_t> samples(2 * pop.diploids.size());
            std::iota(samples.begin(), samples.end(), 0);
            fwdpp::ts::count_mutations(pop.tables, pop.mutations, samples,
                                       pop.mcounts);
        }
    else
        {
            fwdpp::fwdpp_internal::process_haploid_genomes(
                pop.haploid_genomes, pop.mutations, pop.mcounts);
        }
}

