/**
* Module Hierarchy Example :
* mod_1 -> mod_11 -> mod_111 .
* Inheritance across Hierarchy :
* mod_2 inherits mod_1.mod_11 ,
* mod_3.mod_31 inherits mod_1.mod_11 ,
* mod_4 inherits mod_3.mod_31, mod_2 ,
* mod_5 inherits mod_1 and mod_1.mod_11
*/

EXPORT example_6 := MODULE
	IMPORT example_3;

	EXPORT mod_1 := MODULE
		EXPORT v1_m1 := 2.4;
		EXPORT mod_11(real8 a_11) := MODULE
			EXPORT v1_m11 := 2.5 * a_11 + v1_m1;
			EXPORT mod_111(real8 a_111) := MODULE
				EXPORT v1_m111 := 2.6 * a_11 * a_111 + v1_m1 + v1_m11;
			END;
		END;
	END;

	EXPORT mod_2 := MODULE(mod_1.mod_11(2.3))
		EXPORT v1_m2 := 2.9;
	END;

	EXPORT mod_3 := MODULE
		EXPORT v1_m3 := 3.0;
		EXPORT mod_31 := MODULE(mod_1.mod_11(2.3))
			EXPORT v1_m31 := 3.1 * v1_m11 + mod_111(3.2).v1_m111;
		END;
	END;

	EXPORT mod_4 := MODULE(mod_3.mod_31, mod_2)
		EXPORT v1_m4 := 3.3;
	END;

	EXPORT mod_5 := MODULE(mod_1, mod_1.mod_11(2.4))
		EXPORT v1_m5 := 3.7;
	END;
END;
