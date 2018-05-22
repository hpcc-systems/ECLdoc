/**
* Example : Inheritance across files
* mod_1 in Example_4 inherits mod_1 in Example_3
*/

EXPORT Example_3 := MODULE
	EXPORT mod_1 := MODULE
		EXPORT v1_m1 := 2.5;
		EXPORT v2_m1_ex3 := 2.3;
	END;
END;