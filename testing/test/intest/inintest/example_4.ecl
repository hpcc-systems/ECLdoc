IMPORT example_3.mod_1 as mod_1_ex3;

/**
* Example : Inheritance across files
* mod_1 in Example_4 inherits mod_1 in Example_3
*/

EXPORT example_4 := MODULE
	EXPORT mod_1 := MODULE(mod_1_ex3)
		EXPORT v2_m1_ex4 := v2_m1_ex3 * 2;
	END;
END;
