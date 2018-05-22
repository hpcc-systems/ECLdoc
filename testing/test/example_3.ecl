/**
* Documentation Testing
* Multiline Title.
* link@myspace.com
* <p>
* Sentence 1
* blablalbla                    bbblaaaa
* <p>
* Sentence 2
* <pre>
* blablalbla                    bbbblaaaaa
*
* bblaaaaaaaaaa
* </pre>
*   @param first okay_1
*   @param second okay_2
*   @param third okay_3
*   @field f1 oka_f1
*   @field f2 oka_f2
*   @return rec_1
*   @see example_1.mod_1
*   @author example_1.sarthakjain
*/
 EXPORT Example_3 := MODULE
    EXPORT mod_1 := MODULE
    	/** Doc test 2. Title end by
        * period not newline
    	* <pre>
    	* ABCD ||||
    	* CDEF ||||
    	*/
        EXPORT v1_m1 := 2.5;
        /** DOC Test 3
        * No Period title
        */
        EXPORT v2_m1_ex3 := 2.3;
        EXPORT REAL8 abc(REAL8 x) := x * 2.0;
        EXPORT long_name(DATASET({REAL8 u}) X, DATASET({REAL8 u}) IntW, DATASET({REAL8 u}) Intb, REAL8 BETA=0.1, REAL8 sparsityParam=0.1 , REAL8 LAMBDA=0.001, REAL8 ALPHA=0.1, UNSIGNED2 MaxIter=100) := 2.3;
    END;
END;