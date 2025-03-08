import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])       
    # data[name] = {
                # "name": name,
                # "mother": row["mother"] or None,
                # "father": row["father"] or None,
                # "trait": (True if row["trait"] == "1" else
                #           False if row["trait"] == "0" else None)

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.
    """

    probability = 1  # 初始化联合概率

    for person in people:
        gene_count = (
            1 if person in one_gene else 2 if person in two_genes else 0
        )  # 确定当前人的基因数量

        # 计算该人的 `P(trait | 基因数)`
        trait_prob = PROBS["trait"][gene_count][person in have_trait]

        # 计算 `P(基因数 | 父母基因数)`
        mother = people[person]["mother"]
        father = people[person]["father"]

        if mother is None and father is None:
            # 父母未知，使用 **基因先验概率**
            gene_prob = PROBS["gene"][gene_count]
        else:
            # 父母已知，使用 **Mendel 遗传规则**
            mother_gene_count = (
                1 if mother in one_gene else 2 if mother in two_genes else 0
            )
            father_gene_count = (
                1 if father in one_gene else 2 if father in two_genes else 0
            )

            # 计算母亲和父亲传递基因的概率
            def inherit_prob(parent_gene_count):
                if parent_gene_count == 2:
                    return 1 - PROBS["mutation"]
                elif parent_gene_count == 1:
                    return 0.5
                else:
                    return PROBS["mutation"]

            mother_prob = inherit_prob(mother_gene_count)
            father_prob = inherit_prob(father_gene_count)

            # 计算孩子的基因数
            if gene_count == 0:
                gene_prob = (1 - mother_prob) * (1 - father_prob)
            elif gene_count == 1:
                gene_prob = (mother_prob * (1 - father_prob)) + ((1 - mother_prob) * father_prob)
            else:
                gene_prob = mother_prob * father_prob

        # 更新联合概率
        probability *= gene_prob * trait_prob

    return probability



def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        gene_count = (
            1 if person in one_gene else 2 if person in two_genes else 0
        )

        probabilities[person]["gene"][gene_count] += p
        probabilities[person]["trait"][person in have_trait] += p
    return probabilities



def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        for field in probabilities[person]:
            total = sum(probabilities[person][field].values())
            for value in probabilities[person][field]:
                probabilities[person][field][value] /= total
    return probabilities


if __name__ == "__main__":
    main()
