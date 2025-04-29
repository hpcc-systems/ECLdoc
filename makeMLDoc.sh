#!/bin/sh
# Generate each bundle's documentation

# ML_Core
ecldoc --iroot ~/source/ML_Core --oroot ~/docs/ML_Core --format "html,pdf" --hideInternal

# PBblas
ecldoc --iroot ~/source/PBblas --oroot ~/docs/PBblas --eclcc=" -I ~/source" --exdocpaths ~/docs/ML_Core/xml --format "html,pdf" --exclude "internal/*.ecl,test/*.ecl,performance/*.ecl,ecl/*.ecl" --hideInternal

# The following have dependencies on ML_Core and sometimes PBblas, so we want to stitch those
# together.  We use the --eclcc and exdocpaths options to do that.

# LearningTrees
ecldoc --iroot ~/source/LearningTrees --oroot ~/docs/LearningTrees --eclcc=" -I ~/source" --exdocpaths ~/docs/ML_Core/xml --format "html,pdf" --exclude "internal/*.ecl,test/*.ecl,test/datasets/*.ecl" --hideInternal

# LogisticRegression
ecldoc --iroot ~/source/LogisticRegression --oroot ~/docs/LogisticRegression --eclcc=" -I ~/source" --exdocpaths docs/ML_Core/xml --format "html,pdf" --exclude "IRLS/*.ecl,performance/*.ecl,validation/*.ecl" --hideInternal

# LinearRegression
ecldoc --iroot ~/source/LinearRegression --oroot ~/docs/LinearRegression --eclcc=" -I ~/source" --exdocpaths docs/ML_Core/xml,docs/PBblas/xml --format "html,pdf" --exclude "performance/*.ecl,test/*.ecl,test/Datasets/*.ecl,test/Utils/*.ecl" --hideInternal

# GLM
ecldoc --iroot ~/source/GLM --oroot ~/docs/GLM --eclcc=" -I ~/source" --exdocpaths docs/ML_Core/xml,docs/PBblas/xml --format "html,pdf" --exclude "performance/*.ecl,validation/*.ecl, IRLS/*.ecl,Datasets/*.ecl" --hideInternal

# SupportVectorMachines
ecldoc --iroot ~/source/SupportVectorMachines --oroot ~/docs/SupportVectorMachines --eclcc=" -I ~/source" --exdocpaths "docs/ML_Core/xml" --format "html,pdf" --exclude "Performance/*.ecl,Validation/*.ecl, Datasets/*.ecl, Examples/*.ecl, libsvm/*.ecl" --hideInternal

# KMeans
ecldoc --iroot ~/source/KMeans --oroot ~/docs/KMeans --eclcc=" -I ~/source" --exdocpaths docs/ML_Core/xml,docs/PBblas/xml --format "html,pdf" --exclude "test/*.ecl,test/datasets/*.ecl, test/Performance/*.ecl, test/Validation/*.ecl" --hideInternal

# TextVectors
ecldoc --iroot ~/source/TextVectors --oroot ~/docs/TextVectors --eclcc=" -I ~/source" --exdocpaths ~/docs/ML_Core/xml --format "html,pdf" --exclude "internal/*.ecl,test/*.ecl" --hideInternal

# GNN
ecldoc --iroot ~/source/GNN --oroot ~/docs/GNN --eclcc=" -I ~/source" --exdocpaths ~/docs/ML_Core/xml --format "html,pdf" --exclude "Internal/*.ecl,Test/*.ecl,Test/HARTests/*.ecl" --hideInternal

# DBSCAN
ecldoc --iroot ~/source/dbscan --oroot ~/docs/dbscan --eclcc=" -I ~/source" --exdocpaths ~/docs/ML_Core/xml --format "html,pdf" --exclude "internal/*.ecl,tests/*.ecl,tests/datasets/*.ecl" --hideInternal

# HPCC-Causality
ecldoc --iroot ~/source/HPCC_Causality --oroot ~/docs/HPCC_Causality --eclcc=" -I ~/source"  --format "html,pdf" --exclude "internal/*.ecl,Test/*.ecl,Test/Causality/*.ecl,Test/Probability/*.ecl,Test/Synth/*.ecl,performance/*.ecl,ecl/*.ecl" --hideInternal

# Now we copy the resulting index.pdf files to files in our publish area named correctly for each bundle.

cp -f ~/docs/ML_Core/tex/index.pdf ~/share/Publish/ML_Core.pdf
cp -f ~/docs/PBblas/tex/index.pdf ~/share/Publish/PBblas.pdf
cp -f ~/docs/LinearRegression/tex/index.pdf ~/share/Publish/LinearRegression.pdf
cp -f ~/docs/LogisticRegression/tex/index.pdf ~/share/Publish/LogisticRegression.pdf
cp -f ~/docs/LearningTrees/tex/index.pdf ~/share/Publish/LearningTrees.pdf
cp -f ~/docs/GLM/tex/index.pdf ~/share/Publish/GLM.pdf
cp -f ~/docs/SupportVectorMachines/tex/index.pdf ~/share/Publish/SupportVectorMachines.pdf
cp -f ~/docs/KMeans/tex/index.pdf ~/share/Publish/KMeans.pdf
cp -f ~/docs/TextVectors/tex/index.pdf ~/share/Publish/TextVectors.pdf
cp -f ~/docs/GNN/tex/index.pdf ~/share/Publish/GNN.pdf
cp -f ~/docs/dbscan/tex/index.pdf ~/share/Publish/dbscan.pdf
cp -f ~/docs/HPCC_Causality/tex/index.pdf ~/share/Publish/HPCC_Causality.pdf

