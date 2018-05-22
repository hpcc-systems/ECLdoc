/**
* Basic Inheritance documentation :
* mod_3 inherits both mod_1 and mod_2 .
* Inherits v2_m1, v2_m2,
* Overrides v1_m1,
* new locals v2_m3 .
* Interface Inheritance :
* mod_4 inherits interface iface_1,
* overrides v1_i1
*/

EXPORT example_2 := MODULE

	EXPORT rec_1 := RECORD
		Real8 v1;
	END;

	EXPORT rec_2 := RECORD(rec_1)
		Real8 v2;
	END;

	EXPORT rec_3 := RECORD
		rec_1;
		Real8 v3;
	END;

	EXPORT mod_1 := MODULE, VIRTUAL
		EXPORT real8 v1_m1;
		EXPORT v2_m1 := 9.9;
	END;

	EXPORT mod_2 := MODULE
		EXPORT v1_m1 := 10.0;
		EXPORT v2_m2 := 9.7;
	END;

	EXPORT mod_3 := MODULE(mod_1, mod_2)
		EXPORT v1_m1 := 9.0;
		EXPORT v2_m3 := 9.9;
	END;

	EXPORT iface_1 := INTERFACE
		EXPORT real8 v1_i1;
	END;

	EXPORT mod_4 := MODULE(iface_1)
		EXPORT v1_i1 := 34.9;
		EXPORT STRING20 v2_m4 := 'TEST';
	END;
END;
