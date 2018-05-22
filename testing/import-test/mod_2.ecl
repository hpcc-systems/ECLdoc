IMPORT mod_1;

EXPORT mod_2 := MODULE
	EXPORT v2 := mod_1;
	EXPORT v3 := mod_1.v1;
	EXPORT v4(REAL8 a2) := mod_1.m1v4(2.0);
	EXPORT v5 := mod_1.m1v4(3.0).m1v5;
	EXPORT v6 := mod_1.m1v6;
END;
