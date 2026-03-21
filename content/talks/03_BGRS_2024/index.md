---
title: "Conference talk on data sanity-driven approach in plant Genomics on BGRS-2024, Novosibirsk" 
date: 2024-07-27
tags: ["plastid genome","plastome","phylogeny","comparative genomics","data quality","biopython"]
author: ["Asan Emirsaliev"]
description: "A talk on the importance of data quality in plant genomics."
summary: "The description of the approach that aims to fix data inconsistency issues in comparative studies of plastid genomes."
#editPost:
#    URL: "https://github.com/pmichaillat/hugo-website"
#    Text: "GitHub repository"
showToc: true
disableAnchoredHeadings: false

---
The talk title was "A unified data preprocessing framework to address inconsistencies in comparative plastid genome studies".

With the rise of high-throughput sequencing technologies, the amount of genomic data available to researchers has exploded. This has opened new avenues for large-scale comparative phylogenetic studies.

Plastids are small organelles within a plant cell that harbor its own DNA. Plastid genomes were widely used in plant phylogeny studies and still do play a central role in understanding plant evolution. The plastid genome, so called as plastome, is relatively short and higly conserved among land plants. These makes it the excellent source of data for resolving plant phylogeny.

A typical plastid phylogenomic study involves multiple stages: genome assembly, data retrieval, dataset construction, multiple sequence alignment, and tree reconstruction. The error may appear at any of these stages. Today we’ll be discussing approaches for the very initial step - the data preparation and dataset construction.

During four decades of plastome sequence data collecting, standards were rapidly evolved, leading to data inconsistencies within databases, especially in relation to the genome structure,  annotation, metadata, record duplications. Those issues decrease the quality of the data that may affect the analysis. Here we rely on the core rule of data science - if you pass a garbage in, you obtain also a garbage in the output.

To address these issues, it’s essential to follow a series of standardized procedures that ensure data consistency and comparability. This is where our proposed framework comes into play. Each step is implemented in notebook environment using Biopython, Pandas and Jupyter Notebook.

We argue for automatization, reproducibility and programmatic solutions. So the data should also be retrieved via Entrez. But a query to the Nucletide database should cover all possible naming patterns.

The query should be constructed so that the response contain the entire plastome data only. Partial sequences should be excluded at the query step.

The framework was implemented while preparing Cichorieae plastid data to the analysis. Most records were duplicated due to the presence in both GenBank and RefSeq databases. We perform record deduplication to eliminate any redundant entries.

Because of the long story of sequence annotating, multiple names were used for the same gene. Resolving it is a kind of challenge, and in a relatively small dataset we noted synonimous names.

Plastid genome has quadripartite structure and contain two inverted repeats, devided by single copy regions. There are several options how the features were labeled and categorized basing on GenBank standard types before uploading to database.

Some of this annotations might also be missed. An Absence of the feature in annotation in most cases indicates to the pure annotation rather the physical absence of the feature in the sequence.

Inverted repeat junction sites positions are required by some kind of analyses. So the records involved in the analysis should be consistently annotated in part of inverted repeats. But in our sample study of the Crepidinae subtribe, we found a range of annotation issues.

We perform batch reannotation of the records. Different tools were tested, and they can also be used in combination.

A plastid genome assembly result in a graph where inverted repeats connects two loops of large and small single copy regions. It can resolved in different ways. But the truth is that at the same time circular molecule of plastid genome is presented in different structural isoforms within the same cell. They differ by orientation of these regions. There are an unofficial agreement for accessions that are deposited to databases to follow the structure of the first published plastid genome.

For the purpose of the sequence comparison, the second copy of the repeat should be excluded. But you can see that some genes are truncated at the junction of repeats, and in the standard isoform the SSC region should be reverse-complemented.

If you perform manual curation of the annotation, some tools might brake the genbank file. The metadata fields should be filled again.

{{< embed-pdf url="framework_2024-07-27.pdf" hideLoader="true" >}}

The abstract was published at the conference proceedings book.
