#!/bin/sh
# Shell script to Generate Documentation for all Machine-Learning Bundles

# Generate each bundle's documentation
ecldoc --iroot ~/pcsource/ML_Core --oroot ~/share/docs/ML_Core --format "html,pdf" --hideInternal

ecldoc --iroot ~/pcsource/PBblas --oroot ~/share/docs/PBblas --eclcc=" -I ~/pcsource" --exdocpaths ~/share/docs/ML_Core/xml --format "html,pdf" --exclude "internal/*.ecl,test/*.ecl,performance/*.ecl,ecl/*.ecl" --hideInternal

# The following have dependencies on ML_Core and sometimes PBblas, so we want to stitch those
# together.  We use the --eclcc and --exdocpaths options to do that.

ecldoc --iroot ~/pcsource/LearningTrees --oroot ~/share/docs/LearningTrees --eclcc=" -I ~/pcsource" --exdocpaths ~/share/docs/ML_Core/xml --format "html,pdf" --exclude "internal/*.ecl,test/*.ecl,test/datasets/*.ecl" --hideInternal

ecldoc --iroot ~/pcsource/LogisticRegression --oroot ~/share/docs/LogisticRegression --eclcc=" -I ~/pcsource" --exdocpaths ~/share/docs/ML_Core/xml --format "html,pdf" --exclude "IRLS/*.ecl,performance/*.ecl,validation/*.ecl" --hideInternal

ecldoc --iroot ~/pcsource/LinearRegression --oroot ~/share/docs/LinearRegression --eclcc=" -I ~/pcsource" --exdocpaths "/home/tetrapod/share/docs/ML_Core/xml,/home/tetrapod/share/docs/PBblas/xml" --format "html,pdf" --exclude "performance/*.ecl,test/*.ecl,test/Datasets/*.ecl,test/Utils/*.ecl" --hideInternal

ecldoc --iroot ~/pcsource/GLM --oroot ~/share/docs/GLM --eclcc=" -I ~/pcsource" --exdocpaths "/home/tetrapod/share/docs/ML_Core/xml,/home/tetrapod/share/docs/PBblas/xml" --format "html,pdf" --exclude "performance/*.ecl,validation/*.ecl, IRLS/*.ecl,Datasets/*.ecl" --hideInternal

ecldoc --iroot ~/pcsource/SupportVectorMachines --oroot ~/share/docs/SupportVectorMachines --eclcc=" -I ~/pcsource" --exdocpaths "/home/tetrapod/share/docs/ML_Core/xml" --format "html,pdf" --exclude "Performance/*.ecl,Validation/*.ecl, Datasets/*.ecl, Examples/*.ecl, libsvm/*.ecl" --hideInternal

# Now we copy the resulting index.pdf files to files in our publish area named correctly for each bundle.

cp -f ~/share/docs/ML_Core/tex/index.pdf ~/share/Publish/ML_Core.pdf
cp -f ~/share/docs/PBblas/tex/index.pdf ~/share/Publish/PBblas.pdf
cp -f ~/share/docs/LinearRegression/tex/index.pdf ~/share/Publish/LinearRegression.pdf
cp -f ~/share/docs/LogisticRegression/tex/index.pdf ~/share/Publish/LogisticRegression.pdf
cp -f ~/share/docs/LearningTrees/tex/index.pdf ~/share/Publish/LearningTrees.pdf
cp -f ~/share/docs/GLM/tex/index.pdf ~/share/Publish/GLM.pdf
cp -f ~/share/docs/SupportVectorMachines/tex/index.pdf ~/share/Publish/SupportVectorMachines.pdf