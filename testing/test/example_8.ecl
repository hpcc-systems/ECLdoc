/**
* Three level Hierarchy Example .
* Inheritance across Hierarchy .
* Problems with Type System --
* PROJECT Expression does not maintain record typename (rec_2)
* but do maintain record structure .
* IE mod_2.v1_m2 should be <Table of rec_2> but shown <Table of unnamed> .
* <unnamed> has same structure as record <rec_2> .
*/


EXPORT example_8 := MODULE
	EXPORT mod_1 := MODULE
		EXPORT rec_1 := RECORD
			REAL8 a;
		END;
		EXPORT mod_11 := MODULE
			EXPORT v1_m11 := DATASET([{2.3}], rec_1);
		END;
	END;

	EXPORT mod_2 := MODULE(mod_1.mod_11)
		EXPORT rec_2 := RECORD
			REAL8 b;
		END;
		EXPORT v1_m2(REAL8 ag_1) := PROJECT(v1_m11, TRANSFORM(rec_2, SELF.b := LEFT.a + ag_1));
	END;

END;
