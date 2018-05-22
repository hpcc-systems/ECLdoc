IMPORT example_8;
IMPORT example_8.mod_1 as mod_1;

/**
* Basic ECL without enclosing module
* Multilevel imports Example
*/

mod_2 := example_8.mod_2;

rec_3 := RECORD(mod_2.rec_2)
	REAL8 c;
END;

a := DATASET([{2.3}, {3.4}], mod_1.rec_1);
b := mod_2.v1_m2(80.0);
c := PROJECT(b, TRANSFORM(mod_1.rec_1, SELF.a := LEFT.b));

OUTPUT(c);